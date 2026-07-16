
def test_valid(cldf_dataset, cldf_sqlite_database, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)
    assert cldf_sqlite_database.query('select count(*) from languagetable')[0][0] >= 2000
