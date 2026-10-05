import pytest
from best_served_warm.coffee import Coffee, RECIPES
from best_served_warm import storage


def hold(c, action, frames):
    for _ in range(frames):
        c.work(0.1, action)


def prepare(c):
    c.choose('vessel', c.order['vessel'])
    assert c.next_step()
    c.choose('beans', c.order['beans'])
    assert c.next_step()
    hold(c, 'grind', 21)
    hold(c, 'tamp', 12)
    c.release('tamp')
    hold(c, 'brew', 30)
    c.release('brew')


@pytest.mark.parametrize('index', range(len(RECIPES)))
def test_each_order_can_be_prepared_and_served(index):
    c = Coffee(order_index=index)
    prepare(c)
    assert c.stage == 4
    for key in ('milk', 'syrup', 'straw', 'pastry'):
        assert c.choose(key, c.order[key])
    c.ice = c.order['ice']
    assert c.serve()
    assert c.rating == 5
    assert c.served == 1 and c.earnings == 8
    assert not c.serve()  # No duplicate payment.
    c.reset_drink(next_order=True)
    assert c.stage == 0 and c.order_index == index + 1
    assert c.served == 1 and c.earnings == 8
    assert c.vessel == '' and c.brew == 0


def test_steps_cannot_be_skipped_and_supplies_lock_after_grinding():
    c = Coffee()
    assert not c.next_step()
    assert not c.serve()
    c.work(0.1, 'brew')
    assert c.brew == 0
    assert not c.choose('milk', 'oat')
    c.choose('vessel', 'mug')
    c.next_step()
    assert not c.next_step()
    c.choose('beans', 'medium')
    c.next_step()
    assert not c.choose('beans', 'light')
    c.release('tamp')
    assert c.stage == 2


def test_poor_preparation_affects_feedback_even_with_correct_ingredients():
    c = Coffee()
    c.choose('vessel', 'mug'); c.next_step()
    c.choose('beans', 'medium'); c.next_step()
    c.grind_size = 'coarse'
    hold(c, 'grind', 21)
    hold(c, 'tamp', 3); c.release('tamp')
    hold(c, 'brew', 10); c.release('brew')
    c.choose('milk', 'whole'); c.choose('pastry', 'croissant')
    c.serve()
    assert c.rating == 2
    assert 'fine grind' in c.result
    assert 'green zone' in c.result
    assert '32-40g' in c.result


@pytest.mark.parametrize('point', ['grind', 'tamp', 'brew', 'finish', 'receipt'])
def test_preparation_save_roundtrip(point, tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'data_dir', lambda: tmp_path)
    c = Coffee(vessel='tall', beans='light', stage=2)
    hold(c, 'grind', 8 if point == 'grind' else 21)
    if point != 'grind':
        hold(c, 'tamp', 12)
    if point not in ('grind', 'tamp'):
        c.release('tamp'); hold(c, 'brew', 30)
    if point in ('finish', 'receipt'):
        c.release('brew'); c.choose('milk', 'oat'); c.ice = True
    if point == 'receipt':
        c.serve()
    saved = storage.DEFAULT_GAME | dict(scene='coffee', page=0, revealed=0.0, coffee=c.to_dict())
    storage.save_game(saved)
    restored = Coffee.from_dict(storage.load_game()['coffee'])
    assert restored == c


@pytest.mark.parametrize('patch', [dict(stage=8), dict(grind=float('nan')), dict(grind_size='sand'), dict(stage=3), dict(served=-1), dict(ice='yes')])
def test_invalid_saves_are_rejected(patch):
    with pytest.raises(ValueError):
        Coffee.from_dict(Coffee().to_dict() | patch)
