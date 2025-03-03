from typing import Set
import pytest
from gene_finder.pipeline import Pipeline
import subprocess
import tempfile


def mmseqs_db(tmp_dir, fasta, db_name):
    # convert protein sequences to an mmseqs formatted database
    db = f"{tmp_dir.name}/{db_name}"
    subprocess.run(["mmseqs", "createdb", fasta, db], check=True)
    return db


def diamond_db(tmp_dir, fasta, db_name):
    # convert protein sequences to a diamond formatted database
    db = f"{tmp_dir.name}/{db_name}"
    subprocess.run(["diamond", "makedb", "--in", fasta, "-d", db], check=True)
    return db


def test_seed_with_coordinates_step1():
    # use fasta2 and the cas.prot database from e2e tests
    data = "tests/integration/integration_data/end-to-end/fasta2.fasta"
    db = "tests/integration/integration_data/end-to-end/cas.prot"
    p = Pipeline()
    p.add_seed_with_coordinates_step(db=db, name="test1", e_val=0.001, blast_type="PROT")
    results = p.run(job_id="coord_test_1", data=data, output_directory="/tmp")
    assert(len(results) == 2)
    assert "Loc_0-14213" in results["fasta2_1"]
    genes_names = [hit["Hit_name"] for hit in results["fasta2_1"]["Loc_0-14213"]["Hits"].values()]
    assert "cas9" in genes_names


def test_seed_with_coordinates_step2():
    # use fasta2 and the cas.prot database from e2e tests
    data = "tests/integration/integration_data/end-to-end/fasta2.fasta"
    db = "tests/integration/integration_data/end-to-end/cas.prot"
    p = Pipeline()
    p.add_seed_with_coordinates_step(db=db, name="test1", e_val=0.001, blast_type="PROT", start=100, end=14000, contig_id="fasta2_1")
    results = p.run(job_id="coord_test_2", data=data, output_directory="/tmp")
    assert(len(results) == 1)
    assert "Loc_100-14000" in results["fasta2_1"]
    genes_names = [hit["Hit_name"] for hit in results["fasta2_1"]["Loc_100-14000"]["Hits"].values()]
    assert "cas9" in genes_names
    

def test_blastn():
    # This contig contains a single tRNA sequence, along with a few Cas proteins.
    # We just want to confirm that we can find nucleotide sequences using blastn
    data = "tests/integration/integration_data/contigs/trna.fasta"
    db = "tests/integration/integration_data/blast_databases/trna/trnas.fa"
    cas_db = "tests/integration/integration_data/end-to-end/cas.prot"
    p = Pipeline()
    p.add_seed_with_coordinates_step(cas_db, 'cas', 1e-3, 'PROT', parse_descriptions=True, start=0, end=93930, contig_id='test_with_one_trna')
    p.add_blastn_step(db, "test", 1e-10, False)
    results = p.run(job_id="blast_test", data=data, output_directory="/tmp")
    hit = results['test_with_one_trna']['Loc_0-93930']['Hits']['Test_hit-0']
    assert hit['Hit_accession'] == 'Porphyromonas_gingivalis_W83_chr.trna48-SerGGA'
    assert hit['type'] == 'nucleotide'
    assert hit['Query_seq'] == 'CGGAGAGAACAGGATTCGAACCTGCGAACCGGTTTTGCCGGTTACACGCTTTCCAGGCGTGCCTCTTCAACCACTCGAGCACCTCTCC'


@pytest.mark.mmseqs
def test_mmseqs():
    # The contig (V. crassostreae s. J520 full genome) contains cas7 & tniQ around position ~85000
    # We are just testing that we can identify this region using mmseqs as the search tool
    tmp_dir = tempfile.TemporaryDirectory()
    cas7_db = mmseqs_db(tmp_dir, "tests/integration/integration_data/blast_databases/cas7.fasta", "cas7")
    tniQ_db = mmseqs_db(tmp_dir, "tests/integration/integration_data/blast_databases/tniQ.fasta", "tniQ")
    data = "tests/integration/integration_data/contigs/v_crass_J520_whole.fasta"
    p = Pipeline()
    p.add_seed_step(tniQ_db, "tniQ", 0.001, blast_type="mmseqs")
    p.add_filter_step(cas7_db, "cas7", 0.001, blast_type="mmseqs")
    results = p.run(job_id="blast_test", data=data, output_directory="/tmp", span=10000, min_prot_len=60)
    genes_names = [hit["Hit_name"] for hit in results["NZ_CCKB01000071.1"]["Loc_75746-96837"]["Hits"].values()]
    assert set(genes_names) == set(["cas7", "tniQ"])


@pytest.mark.diamond
def test_diamond():
    # The contig (V. crassostreae s. J520 full genome) contains cas7 & tniQ around position ~85000
    # We are just testing that we can identify this region using diamond as the search tool
    tmp_dir = tempfile.TemporaryDirectory()
    cas7_db = diamond_db(tmp_dir, "tests/integration/integration_data/blast_databases/cas7.fasta", "cas7")
    tniQ_db = diamond_db(tmp_dir, "tests/integration/integration_data/blast_databases/tniQ.fasta", "tniQ")
    data = "tests/integration/integration_data/contigs/v_crass_J520_whole.fasta"
    p = Pipeline()
    p.add_seed_step(tniQ_db, "tniQ", 0.001, blast_type="diamond")
    p.add_filter_step(cas7_db, "cas7", 0.001, blast_type="diamond")
    results = p.run(job_id="blast_test", data=data, output_directory="/tmp", span=10000, min_prot_len=60)
    genes_names = [hit["Hit_name"] for hit in results["NZ_CCKB01000071.1"]["Loc_75746-96837"]["Hits"].values()]
    assert set(genes_names) == set(["cas7", "tniQ"])