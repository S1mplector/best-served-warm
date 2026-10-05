import pytest
from best_served_warm.stations import Kitchen, StationError
from best_served_warm import storage


def move(k, item, station):
    k.pickup(item); k.place(station)


def work(k, action, frames):
    k.begin(action)
    for _ in range(frames): k.update(.1)
    k.end()


def shot(k):
    cup=k.take_cup('mug'); k.place('espresso')
    work(k,'grind',26)
    move(k,'filter','tamp'); work(k,'tamp',12)
    move(k,'filter','espresso'); work(k,'brew',30)
    return cup


def test_full_station_order_and_cleaning():
    k=Kitchen(); cup=shot(k)
    assert k.filter.dirty
    move(k,cup,'milk'); k.fill_milk('whole'); work(k,'steam',30); k.pour_milk()
    move(k,cup,'finish'); k.add('pastry','croissant')
    move(k,cup,'serve'); assert k.serve()==5
    assert k.served==1 and k.earnings==8 and not k.cups
    move(k,'filter','sink'); k.rinse('filter'); move(k,'filter','grinder')
    move(k,'pitcher','sink'); k.rinse('pitcher'); move(k,'pitcher','milk')
    assert not k.filter.dirty and k.filter.dose==0 and not k.pitcher.dirty


def test_preparation_is_not_tied_to_a_menu_sequence():
    k=Kitchen()
    # Prepare milk and grind before a cup even exists.
    k.fill_milk('oat'); work(k,'steam',28); work(k,'grind',26)
    cup=k.take_cup('tall'); k.place('finish'); k.add('ice',True); k.add('syrup','vanilla')
    move(k,cup,'milk'); k.pour_milk(); move(k,cup,'espresso')
    move(k,'filter','tamp'); work(k,'tamp',12); move(k,'filter','espresso'); work(k,'brew',30)
    assert k.cups[cup].drink.ice and k.cups[cup].drink.milk=='oat'


def test_invalid_transfers_and_missing_tools_do_not_change_state():
    k=Kitchen()
    with pytest.raises(StationError): k.begin('brew')
    cup=k.take_cup('mug')
    with pytest.raises(StationError): k.pickup('filter')
    with pytest.raises(StationError): k.place('grinder')
    assert k.carrying==cup
    k.place('espresso')
    second=k.take_cup('tall')
    with pytest.raises(StationError): k.place('espresso')
    assert k.carrying==second


def test_used_filter_and_pitcher_need_rinsing():
    k=Kitchen(); cup=shot(k)
    move(k,cup,'milk'); k.fill_milk('whole'); k.pour_milk()
    with pytest.raises(StationError): k.fill_milk('oat')
    move(k,'filter','grinder')
    with pytest.raises(StationError): k.begin('grind')


def test_pause_and_save_restore_a_partial_shot(tmp_path, monkeypatch):
    monkeypatch.setattr(storage,'data_dir',lambda:tmp_path)
    k=Kitchen(); cup=k.take_cup('mug'); k.place('espresso')
    work(k,'grind',26); move(k,'filter','tamp'); work(k,'tamp',12); move(k,'filter','espresso')
    k.begin('brew')
    for _ in range(10): k.update(.1)
    k.suspend(); before=k.cups[cup].drink.brew; k.update(.1)
    assert k.cups[cup].drink.brew==before
    saved=storage.DEFAULT_GAME | dict(scene='coffee',page=0,revealed=0.0,kitchen=k.to_dict())
    storage.save_game(saved)
    restored=Kitchen.from_dict(storage.load_game()['kitchen'])
    assert restored.to_dict()==k.to_dict()
    with pytest.raises(StationError): restored.pickup('filter')
    restored.begin('brew')
    for _ in range(20): restored.update(.1)
    restored.end()
    assert round(restored.cups[cup].drink.brew*48)==36


def test_multiple_cups_keep_separate_contents():
    k=Kitchen(); first=k.take_cup('tall'); k.place('finish'); k.add('ice',True)
    second=k.take_cup('mug'); k.place('milk'); k.fill_milk('whole'); k.pour_milk()
    assert not k.cups[second].drink.ice
    assert k.cups[first].drink.milk=='none'
    assert Kitchen.from_dict(k.to_dict()).to_dict()==k.to_dict()
