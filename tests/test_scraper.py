from __future__ import annotations

from datetime import datetime

from app.parser import parse_csv_response, parse_html_response


def test_parse_csv_response() -> None:
    csv_text = "date,draw,clubs,diamonds,hearts,spades,\n25/06/2026,53125,A,J,K,A,\n"
    draws = parse_csv_response(csv_text, datetime(2026, 6, 26, 8, 0, 0))
    assert len(draws) == 1
    assert draws[0].draw_id == 53125
    assert draws[0].date == "2026-06-25"
    assert [card.rank for card in draws[0].cards] == ["A", "J", "K", "A"]
    assert [card.suit for card in draws[0].cards] == ["clubs", "diamonds", "hearts", "spades"]


def test_parse_ajax_html_response() -> None:
    html = """
    <li class="archive_list_item chance">
      <div class="archive_list_block chance_number"><div>53125</div></div>
      <div class="archive_list_block date chance">
        <div>25/06/26</div><div>21:00</div>
      </div>
      <div class="archive_list_block card">
        <div class="cat_data_info chance archive"><div><img src="/images/ic_card_clubs.png" alt="תלתן"></div><div>A</div></div>
        <div class="cat_data_info chance archive red"><div><img src="/images/ic_card_diamond.png" alt="יהלום"></div><div>J</div></div>
        <div class="cat_data_info chance archive red"><div><img src="/images/ic_card_hearth.png" alt="לב"></div><div>K</div></div>
        <div class="cat_data_info chance archive"><div><img src="/images/ic_card_peak.png" alt="עלה"></div><div>A</div></div>
      </div>
    </li>
    """
    draws = parse_html_response(html, datetime(2026, 6, 26, 8, 0, 0), source="test")
    assert len(draws) == 1
    assert draws[0].draw_id == 53125
    assert draws[0].time == "21:00"
    assert [card.suit_he for card in draws[0].cards] == ["תלתן", "יהלום", "לב", "עלה"]
