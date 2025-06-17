from moexalgo import ahdata

def test_ahdata():
    files = ahdata.files()
    assert len(files) > 0
    file = files[0]
    data = ahdata.download(dataset=file.dataset, period=file.year_month)
    assert len(list(data)) > 0