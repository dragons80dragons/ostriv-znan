# -*- coding: utf-8 -*-
"""Крок 14. Довозить у manifest кліпи, чий id гра складає на льоту.

Їх не видно пошуком по тексту вставок: id збирається в коді
(`'hw_'+uaId(w)`, `` `th_${u[0]}_${k}` ``), тож перелік знято з ЖИВОЇ гри —
прогоном усіх 52 островів по 120 разів на кожному рівні в браузері.
Саме цей перелік і є істиною: це рівно ті імена файлів, які гра шукатиме.

Перевірено там само: жоден id не звучить двома різними текстами (була така
вада — одна позначка на задачу з випадковими числами) і жоден не порожній.
Ідемпотентний.
"""
import io, json, os

MAN = r'G:\ostriv-znan\tools\manifest.json'
ITEMS = {
 "a_ni": "ні", "a_tak": "так",
 "aq_brat": "У тебе є брат?", "aq_druh": "Як звати твого друга?",
 "aq_hodyna": "А котра саме година?", "aq_kit": "Це кіт?",
 "aq_lito": "Що ти робив улітку?", "aq_lystia": "Чому восени падає листя?",
 "aq_velyka": "Ти сказав про велику чи малу?", "aq_yabluka": "Ти любиш яблука?",
 "bn_orhanika": "органіка", "bn_papir": "папір", "bn_plastyk": "пластик", "bn_sklo": "скло",
 "ct_kyiv": "Київ", "ct_lviv": "Львів", "ct_odesa": "Одеса",
 "hw_doroha": "дорога", "hw_kvitka": "квітка", "hw_mama": "мама", "hw_moloko": "молоко",
 "hw_raketa": "ракета", "hw_ryba": "риба", "hw_sumka": "сумка", "hw_voda": "вода",
 "in_dotyk_0": "гаряче", "in_dotyk_1": "шорстке", "in_dotyk_2": "мʼяке", "in_dotyk_3": "холодне",
 "in_niukh_0": "запах хліба", "in_niukh_1": "дим", "in_niukh_2": "квіти",
 "in_slukh_0": "пісня", "in_slukh_1": "дзвінок", "in_slukh_2": "грім", "in_slukh_3": "голос",
 "in_smak_0": "солодке", "in_smak_1": "кисле", "in_smak_2": "солоне",
 "in_zor_0": "малюнок", "in_zor_1": "колір", "in_zor_2": "світлофор", "in_zor_3": "усмішка",
 "iv_kholodylnyk": "холодильник", "iv_knyzhka": "книжка", "iv_koleso": "колесо",
 "iv_lampa": "лампа", "iv_litak": "літак", "iv_telefon": "телефон",
 "kv_doshka": "дошка", "kv_izhak": "їжак", "kv_lis": "ліс", "kv_ptakh": "птах",
 "kv_sadok": "садок", "kv_shpakivnia": "шпаківня", "kv_vesna": "весна",
 "kv_vyshnia": "вишня", "kv_zyma": "зима",
 "ky_nota": "нота", "ky_pauza": "пауза", "ky_skrypkovyj": "скрипковий ключ",
 "no_do": "до", "no_fa": "фа", "no_lia": "ля", "no_mi": "мі",
 "no_re": "ре", "no_si": "сі", "no_sol": "соль",
 "nt_nezhyva": "нежива", "nt_rukotvorna": "рукотворна", "nt_zhyva": "жива",
 "q_action": "Яку дію треба виконати?",
 "q_after": "Яке число йде після цього?", "q_before": "Яке число йде перед цим?",
 "q_code_no": "Закодуй «ні» кольором", "q_code_yes": "Закодуй «так» кольором",
 "q_ones": "Скільки одиниць у цьому числі?",
 "q_step1": "Що робимо перш за все?", "q_stepn": "Що робимо далі?",
 "qv_bizhyt": "біжить", "qv_chervonyj": "червоний", "qv_desiat": "десять",
 "qv_dva": "два", "qv_miakyj": "м’який", "qv_odyn": "один", "qv_piat": "п’ять",
 "qv_pyshe": "пише", "qv_spivaie": "співає", "qv_spyt": "спить",
 "qv_teplyj": "теплий", "qv_velykyj": "великий",
 "sa_itypovilno": "іти повільно", "sa_nechipatyj": "не чіпати й сказати дорослим",
 "sa_pohasytysa": "погасити самому", "sa_rozibratys": "розібрати, що всередині",
 "sa_rozpovisty": "розповісти йому адресу", "sa_shvydkoper": "швидко перебігти",
 "sa_sistyjpoik": "сісти й поїхати", "sa_skhovatysi": "сховатися під ліжко",
 "sa_stoiatyjch": "стояти й чекати", "sa_uziatydodo": "узяти додому",
 "sa_vidmovytys": "відмовитись і відійти", "sa_vyjtyjpokl": "вийти й покликати дорослих",
 "sr_dovikna": "до вікна", "sr_napodviria": "на подвірʼя",
 "sr_nezakhodyt": "не заходити туди", "sr_obijtypokr": "обійти по краю",
 "sr_podyvytysi": "подивитися зблизька", "sr_tutmozhnah": "тут можна гратися",
 "sr_tutmozhnap": "тут можна переходити дорогу", "sr_tutzupynka": "тут зупинка",
 "sr_vukryttia": "в укриття",
 "th_cm_0": "олівець", "th_cm_1": "гумка", "th_cm_2": "зошит",
 "th_kg_0": "кавун", "th_kg_1": "мішок картоплі", "th_kg_2": "гарбуз",
 "th_l_0": "молоко", "th_l_1": "відро води", "th_l_2": "сік",
 "th_m_0": "кімната", "th_m_1": "двері", "th_m_2": "паркан",
 "ti_doshch": "Дощ", "ti_kazka": "Казка", "ti_kitmurchyk": "Кіт Мурчик",
 "ti_pyrih": "Пиріг", "ti_shkola": "Школа", "ti_vesna": "Весна",
 "ti_virsh": "Вірш", "ti_zahadka": "Загадка", "ti_zyma": "Зима",
 "v_bly": "близько", "v_blyzko": "близько", "v_dal": "далеко", "v_daleko": "далеко",
 "v_den": "день", "v_harnyj": "гарний", "v_khol": "холодний", "v_kholodnyj": "холодний",
 "v_khutko": "хутко", "v_kliuch": "ключ", "v_kosa": "коса", "v_krasyvyj": "красивий",
 "v_lyst": "лист", "v_mal": "малий", "v_malyj": "малий", "v_neveselyj": "невеселий",
 "v_nich": "ніч", "v_nyz": "низький", "v_nyzkyj": "низький", "v_pov": "повільно",
 "v_povilno": "повільно", "v_ruchka": "ручка", "v_shv": "швидко", "v_shvydko": "швидко",
 "v_studenyj": "студений", "v_sumnyj": "сумний", "v_tep": "теплий", "v_teplyj": "теплий",
 "v_vel": "великий", "v_velykyj": "великий", "v_vys": "високий", "v_vysokyj": "високий",
 "v_zdorovennyj": "здоровенний",
}

man = json.load(io.open(MAN, encoding='utf-8'))
voc = man['voice']['items']
add = []
for vid, txt in ITEMS.items():
    if vid in voc:
        continue
    kind = 'phrase' if (len(txt.split()) > 2 or txt.endswith(('?', '!', '.'))) else 'word'
    voc[vid] = [txt, kind]
    add.append(vid)
io.open(MAN + '.tmp', 'w', encoding='utf-8').write(json.dumps(man, ensure_ascii=False, indent=1))
os.replace(MAN + '.tmp', MAN)
print('додано:', len(add), '| усього кліпів:', len(voc))
