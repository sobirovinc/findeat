from django import forms


class GourmetSearchForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'placeholder': 'グルメ名を入力してください。。。',
            'class': 'form-control mr-2'
        }
    ))

    range = forms.ChoiceField(
        required=False,
        choices=[
            ('', ''),
            (1, '300m'),
            (2, '500m'),
            (3, '1000m'),
            (4, '2000m'),
            (5, '3000m')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    genre = forms.ChoiceField(
        required=False,
        choices=[
            ('', ''),
            ('G001', '居酒屋'),
            ('G013', 'ラーメン'),
            ('G004', '和食'),
            ('G005', '洋食'),
            ('G007', '中華'),
            ('G008', '焼肉・ホルモン'),
            ('G016', 'お好み焼き・もんじゃ'),
            ('G002', 'ダイニングバー・バル'),
            ('G011', 'カラオケ・パーティ'),
            ('G017', '韓国料理'),
            ('G006', 'イタリアン・フレンチ'),
            ('G009', 'アジア・エスニック料理'),
            ('G010', '各国料理'),
            ('G003', '創作料理'),
            ('G012', 'バー・カクテル'),
            ('G014', 'カフェ・スイーツ'),
            ('G015', 'その他グルメ')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    budget = forms.ChoiceField(
        required=False,
        choices=[
            ('', ''),
            ('B009', '~500円'),
            ('B010', '501~1000円'),
            ('B011', '1001～1500円'),
            ('B001', '1501～2000円'),
            ('B002', '2001～3000円'),
            ('B003', '3001～4000円'),
            ('B008', '4001～5000円'),
            ('B004', '5001～7000円'),
            ('B005', '7001～10000円'),
            ( 'B006', '10001～15000円'),
            ('B012', '15001～20000円'),
            ('B013', '20001～30000円'),
            ('B014', '30001円～'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # budget = forms.ChoiceField(
    #     required=False,
    #     choices=[
    #         ('', '',),
    #         ('cheap', '¥'),
    #         ('medium', '¥¥'),
    #         ('expensive', '¥¥¥'),
    #     ],
    #     widget=forms.Select(attrs={'class': 'form-control'})
    # )

    party_capacity = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '宴会の最小収容人数を入力してください。。。',
            'class': 'form-control mr-2'
        }
    ))

    parking = forms.BooleanField(required=False, label="駐車場あり")
    credit_card = forms.BooleanField(required=False, label="クレジットカード利用可")










