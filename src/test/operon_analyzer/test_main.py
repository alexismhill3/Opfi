from operon_analyzer.main import Feature, Operon, RuleSet, _serialize_results
import pytest


def test_serialize_results_fail():
    genes = [
            Feature('cas1', (12, 400), 'lcl|12|400|1|-1', 1, 'ACACEHFEF', 4e-19, 'a good gene', 'MCGYVER'),
            Feature('cas2', (410, 600), 'lcl|410|600|1|-1', 1, 'FGEYFWCE', 2e-5, 'a good gene', 'MGFRERAR'),
            Feature('cas4', (620, 1200), 'lcl|620|1200|1|-1', 1, 'NFBEWFUWEF', 6e-13, 'a good gene', 'MLAWPVTLE'),
            ]
    operon = Operon('QCDRTU', 0, 3400, genes)
    rs = RuleSet() \
        .exclude('cas3') \
        .require('cas12a')
    result = rs.evaluate(operon)
    actual = "\n".join(_serialize_results(rs, [result]))
    expected = "# exclude:cas3,require:cas12a\nQCDRTU,0..3400,fail require:cas12a"
    assert actual == expected


@pytest.mark.parametrize('gene1_start,gene1_end,gene2_start,gene2_end,distance_bp,expected', [
    (12, 400, 410, 600, 20, True),
    (410, 600, 12, 400, 20, True),
    (400, 12, 410, 600, 20, True),
    (12, 400, 600, 410, 20, True),
    (410, 600, 400, 12, 20, True),
    (12, 400, 410, 600, 5, False),
    (410, 600, 12, 400, 5, False),
    (400, 12, 410, 600, 5, False),
    (12, 400, 600, 410, 5, False),
    (410, 600, 400, 12, 5, False),
    ])
def test_max_distance(gene1_start, gene1_end, gene2_start, gene2_end, distance_bp, expected):
    genes = [
            Feature('cas1', (gene1_start, gene1_end), 'lcl|12|400|1|-1', 1, 'ACACEHFEF', 4e-19, 'a good gene', 'MCGYVER'),
            Feature('cas2', (gene2_start, gene2_end), 'lcl|410|600|1|-1', 1, 'FGEYFWCE', 2e-5, 'a good gene', 'MGFRERAR'),
            ]
    operon = Operon('contig', 0, 1000, genes)
    rs = RuleSet().max_distance('cas1', 'cas2', distance_bp)
    result = rs.evaluate(operon)
    assert (result.is_passing is expected)


# def test_parse_input_crispr_repeat():
#     data = ['STDS9ITBSE', '1009983..1031284', 'CRISPR array', '1017560..1017914', '', '', '', '', 'Copies: 6, Repeat: 30, Spacer: 34', '-------------------GATAAACATTAACATAGGATGTATTGAAAC-']


# def test_parse_input_cas_gene():
# data = ['CRISPR-transposases', '1396535..1417167', 'cas11', '1412833..1412048', 'lcl|1412833|1412048|2|-1', '-1', 'UniRef50_UPI0009FEB4C2', '0', 'type I-E CRISPR-associated protein Cse2/CasB n=1 Tax=Actinobaculum sp. oral taxon 183 TaxID=712888 RepID=UPI0009FEB4C2', 'MVRHRPKQSPSYIYHFPTSERERSIVTTVNEIIKDEKPLRKRKRRNLSPIGQKIDCKISCLQKGYLSEDSRKQARARADLANLRRGLTAGPGERVEIWHLTQVDVSDNAPDEPTREEFAVHVSMTLYAAHQQSRTKPMHRPAEGLGHAAHSVVGYGDDENPSARARFDALVMSSTPRELRRHLRSFVSLLRAKEIPLDYGMLVDDIVCFQRPGGAKAVRRHWSRQYYDFSSTDGESSETDSTAEDICSENSLHNSLRNTKE']
