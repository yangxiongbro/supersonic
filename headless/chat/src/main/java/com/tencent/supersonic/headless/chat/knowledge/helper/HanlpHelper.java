package com.tencent.supersonic.headless.chat.knowledge.helper;

import com.google.common.collect.Lists;
import com.hankcs.hanlp.HanLP;
import com.hankcs.hanlp.corpus.tag.Nature;
import com.hankcs.hanlp.dictionary.CoreDictionary;
import com.hankcs.hanlp.dictionary.DynamicCustomDictionary;
import com.hankcs.hanlp.seg.Segment;
import com.hankcs.hanlp.seg.common.Term;
import com.tencent.supersonic.common.pojo.enums.DictWordType;
import com.tencent.supersonic.headless.api.pojo.response.S2Term;
import com.tencent.supersonic.headless.chat.knowledge.DatabaseMapResult;
import com.tencent.supersonic.headless.chat.knowledge.DictWord;
import com.tencent.supersonic.headless.chat.knowledge.EmbeddingResult;
import com.tencent.supersonic.headless.chat.knowledge.HadoopFileIOAdapter;
import com.tencent.supersonic.headless.chat.knowledge.HanlpMapResult;
import com.tencent.supersonic.headless.chat.knowledge.MapResult;
import com.tencent.supersonic.headless.chat.knowledge.MultiCustomDictionary;
import com.tencent.supersonic.headless.chat.knowledge.SearchService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.util.CollectionUtils;
import org.springframework.util.ResourceUtils;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

/** HanLP helper */
@Slf4j
public class HanlpHelper {

    public static final String FILE_SPILT = File.separator;
    public static final String SPACE_SPILT = "#";
    private static volatile DynamicCustomDictionary CustomDictionary;
    private static volatile Segment segment;

    static {
        // reset hanlp config
        try {
            resetHanlpConfig();
        } catch (FileNotFoundException e) {
            log.error("resetHanlpConfig error", e);
        }
    }

    public static Segment getSegment() {
        if (segment == null) {
            synchronized (HanlpHelper.class) {
                if (segment == null) {
                    segment = HanLP.newSegment().enableIndexMode(true).enableIndexMode(4)
                            .enableCustomDictionary(true).enableCustomDictionaryForcing(true)
                            .enableOffset(true).enableJapaneseNameRecognize(false)
                            .enableNameRecognize(false).enableAllNamedEntityRecognize(false)
                            .enableJapaneseNameRecognize(false)
                            .enableNumberQuantifierRecognize(false).enablePlaceRecognize(false)
                            .enableOrganizationRecognize(false)
                            .enableCustomDictionary(getDynamicCustomDictionary());
                }
            }
        }
        return segment;
    }

    public static DynamicCustomDictionary getDynamicCustomDictionary() {
        if (CustomDictionary == null) {
            synchronized (HanlpHelper.class) {
                if (CustomDictionary == null) {
                    CustomDictionary = new MultiCustomDictionary(HanLP.Config.CustomDictionaryPath);
                }
            }
        }
        return CustomDictionary;
    }

    /** reload custom dictionary */
    public static boolean reloadCustomDictionary() throws IOException {

        final long startTime = System.currentTimeMillis();

        if (HanLP.Config.CustomDictionaryPath == null
                || HanLP.Config.CustomDictionaryPath.length == 0) {
            return false;
        }
        if (HanLP.Config.IOAdapter instanceof HadoopFileIOAdapter) {
            // 1.delete hdfs file
            HdfsFileHelper.deleteCacheFile(HanLP.Config.CustomDictionaryPath);
            // 2.query txt files，update CustomDictionaryPath
            HdfsFileHelper.resetCustomPath(getDynamicCustomDictionary());
        } else {
            FileHelper.deleteCacheFile(HanLP.Config.CustomDictionaryPath);
            FileHelper.resetCustomPath(getDynamicCustomDictionary());
        }
        // 3.clear trie
        SearchService.clear();

        boolean reload = getDynamicCustomDictionary().reload();
        if (reload) {
            log.info("Custom dictionary has been reloaded in {} milliseconds",
                    System.currentTimeMillis() - startTime);
        }
        return reload;
    }

    private static void resetHanlpConfig() throws FileNotFoundException {
        if (HanLP.Config.IOAdapter instanceof HadoopFileIOAdapter) {
            return;
        }
        String hanlpPropertiesPath = getHanlpPropertiesPath();

        HanLP.Config.CustomDictionaryPath = Arrays.stream(HanLP.Config.CustomDictionaryPath)
                .map(path -> hanlpPropertiesPath + FILE_SPILT + path).toArray(String[]::new);
        log.info("hanlpPropertiesPath:{},CustomDictionaryPath:{}", hanlpPropertiesPath,
                HanLP.Config.CustomDictionaryPath);

        HanLP.Config.CoreDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CoreDictionaryPath;
        HanLP.Config.CoreDictionaryTransformMatrixDictionaryPath = hanlpPropertiesPath + FILE_SPILT
                + HanLP.Config.CoreDictionaryTransformMatrixDictionaryPath;
        HanLP.Config.BiGramDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.BiGramDictionaryPath;
        HanLP.Config.CoreStopWordDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CoreStopWordDictionaryPath;
        HanLP.Config.CoreSynonymDictionaryDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CoreSynonymDictionaryDictionaryPath;
        HanLP.Config.PersonDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PersonDictionaryPath;
        HanLP.Config.PersonDictionaryTrPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PersonDictionaryTrPath;

        HanLP.Config.PinyinDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PinyinDictionaryPath;
        HanLP.Config.TranslatedPersonDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.TranslatedPersonDictionaryPath;
        HanLP.Config.JapanesePersonDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.JapanesePersonDictionaryPath;
        HanLP.Config.PlaceDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PlaceDictionaryPath;
        HanLP.Config.PlaceDictionaryTrPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PlaceDictionaryTrPath;
        HanLP.Config.OrganizationDictionaryPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.OrganizationDictionaryPath;
        HanLP.Config.OrganizationDictionaryTrPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.OrganizationDictionaryTrPath;
        HanLP.Config.CharTypePath = hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CharTypePath;
        HanLP.Config.CharTablePath = hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CharTablePath;
        HanLP.Config.PartOfSpeechTagDictionary =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PartOfSpeechTagDictionary;
        HanLP.Config.WordNatureModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.WordNatureModelPath;
        HanLP.Config.MaxEntModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.MaxEntModelPath;
        HanLP.Config.NNParserModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.NNParserModelPath;
        HanLP.Config.PerceptronParserModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PerceptronParserModelPath;
        HanLP.Config.CRFSegmentModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CRFSegmentModelPath;
        HanLP.Config.HMMSegmentModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.HMMSegmentModelPath;
        HanLP.Config.CRFCWSModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CRFCWSModelPath;
        HanLP.Config.CRFPOSModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CRFPOSModelPath;
        HanLP.Config.CRFNERModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.CRFNERModelPath;
        HanLP.Config.PerceptronCWSModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PerceptronCWSModelPath;
        HanLP.Config.PerceptronPOSModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PerceptronPOSModelPath;
        HanLP.Config.PerceptronNERModelPath =
                hanlpPropertiesPath + FILE_SPILT + HanLP.Config.PerceptronNERModelPath;
    }

    public static String getHanlpPropertiesPath() throws FileNotFoundException {
        return ResourceUtils.getFile("classpath:hanlp.properties").getParent();
    }

    public static boolean addToCustomDictionary(DictWord dictWord) {
        log.debug("dictWord:{}", dictWord);
        return getDynamicCustomDictionary().insert(dictWord.getWord(),
                dictWord.getNatureWithFrequency());
    }

    public static void removeFromCustomDictionary(DictWord dictWord) {
        log.debug("dictWord:{}", dictWord);
        CoreDictionary.Attribute attribute = getDynamicCustomDictionary().get(dictWord.getWord());
        if (attribute == null) {
            return;
        }
        log.info("get attribute:{}", attribute);
        getDynamicCustomDictionary().remove(dictWord.getWord());
        StringBuilder sb = new StringBuilder();
        List<Nature> natureList = new ArrayList<>();
        for (int i = 0; i < attribute.nature.length; i++) {
            if (!attribute.nature[i].toString().equals(dictWord.getNature())) {
                sb.append(attribute.nature[i].toString() + " ");
                sb.append(attribute.frequency[i] + " ");
                natureList.add((attribute.nature[i]));
            }
        }
        String natureWithFrequency = sb.toString();
        int len = natureWithFrequency.length();
        log.info("filtered natureWithFrequency:{}", natureWithFrequency);
        if (StringUtils.isNotBlank(natureWithFrequency)) {
            getDynamicCustomDictionary().add(dictWord.getWord(),
                    natureWithFrequency.substring(0, len - 1));
        }
        SearchService.remove(dictWord, natureList.toArray(new Nature[0]));
    }

    public static <T extends MapResult> void transLetterOriginal(List<T> mapResults) {
        if (CollectionUtils.isEmpty(mapResults)) {
            return;
        }

        List<T> newResults = new ArrayList<>();

        for (T mapResult : mapResults) {
            String name = mapResult.getName();
            boolean isAdded = false;
            if (MultiCustomDictionary.isLowerLetter(name) && CustomDictionary.contains(name)) {
                CoreDictionary.Attribute attribute = CustomDictionary.get(name);
                if (attribute != null) {
                    isAdded = addLetterOriginal(newResults, mapResult, attribute);
                }
            }

            if (!isAdded) {
                newResults.add(mapResult);
            }
        }
        mapResults.clear();
        mapResults.addAll(newResults);
    }

    public static <T extends MapResult> boolean addLetterOriginal(List<T> mapResults, T mapResult,
            CoreDictionary.Attribute attribute) {
        if (attribute == null) {
            return false;
        }
        boolean isAdd = false;
        if (mapResult instanceof HanlpMapResult) {
            HanlpMapResult hanlpMapResult = (HanlpMapResult) mapResult;
            for (String nature : hanlpMapResult.getNatures()) {
                String orig = attribute.getOriginal(Nature.fromString(nature));
                if (orig != null) {
                    MapResult addMapResult = new HanlpMapResult(orig, Arrays.asList(nature),
                            hanlpMapResult.getDetectWord(), hanlpMapResult.getSimilarity());
                    mapResults.add((T) addMapResult);
                    isAdd = true;
                }
            }
            return isAdd;
        }

        List<String> originals = attribute.getOriginals();
        if (CollectionUtils.isEmpty(originals)) {
            return false;
        }

        if (mapResult instanceof DatabaseMapResult) {
            DatabaseMapResult dbMapResult = (DatabaseMapResult) mapResult;
            for (String orig : originals) {
                DatabaseMapResult addMapResult = new DatabaseMapResult();
                addMapResult.setName(orig);
                addMapResult.setSchemaElement(dbMapResult.getSchemaElement());
                addMapResult.setDetectWord(dbMapResult.getDetectWord());
                mapResults.add((T) addMapResult);
                isAdd = true;
            }
        } else if (mapResult instanceof EmbeddingResult) {
            EmbeddingResult embeddingResult = (EmbeddingResult) mapResult;
            for (String orig : originals) {
                EmbeddingResult addMapResult = new EmbeddingResult();
                addMapResult.setName(orig);
                addMapResult.setDetectWord(embeddingResult.getDetectWord());
                addMapResult.setId(embeddingResult.getId());
                addMapResult.setMetadata(embeddingResult.getMetadata());
                addMapResult.setSimilarity(embeddingResult.getSimilarity());
                mapResults.add((T) addMapResult);
                isAdd = true;
            }
        }

        return isAdd;
    }

    public static List<S2Term> getTerms(String text, Map<Long, List<Long>> modelIdToDataSetIds) {
        return getSegment().seg(text.toLowerCase()).stream()
                .filter(term -> term.getNature().startsWith(DictWordType.NATURE_SPILT))
                .map(term -> transform2ApiTerm(term, modelIdToDataSetIds))
                .flatMap(Collection::stream).collect(Collectors.toList());
    }

    public static List<S2Term> getTerms(List<S2Term> terms, Set<Long> dataSetIds) {
        logTerms(terms);
        if (!CollectionUtils.isEmpty(dataSetIds)) {
            terms = terms.stream().filter(term -> {
                Long dataSetId = NatureHelper.getDataSetId(term.getNature().toString());
                if (Objects.nonNull(dataSetId)) {
                    return dataSetIds.contains(dataSetId);
                }
                return false;
            }).collect(Collectors.toList());
            log.debug("terms filter by dataSetId:{}", dataSetIds);
            logTerms(terms);
        }
        return terms;
    }

    public static List<S2Term> transform2ApiTerm(Term term,
            Map<Long, List<Long>> modelIdToDataSetIds) {
        List<S2Term> s2Terms = Lists.newArrayList();
        List<String> natures = NatureHelper.changeModel2DataSet(String.valueOf(term.getNature()),
                modelIdToDataSetIds);
        for (String nature : natures) {
            S2Term s2Term = new S2Term();
            BeanUtils.copyProperties(term, s2Term);
            s2Term.setNature(Nature.create(nature));
            s2Term.setFrequency(term.getFrequency());
            s2Terms.add(s2Term);
        }
        return s2Terms;
    }

    private static void logTerms(List<S2Term> terms) {
        if (CollectionUtils.isEmpty(terms)) {
            return;
        }
        for (S2Term term : terms) {
            log.debug("word:{},nature:{},frequency:{}", term.word, term.nature.toString(),
                    term.getFrequency());
        }
    }
}
