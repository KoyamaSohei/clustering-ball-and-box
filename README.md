# clustering ball and box

つくばロボットコンテスト2018で作ったボールがどこにあるか認識するプログラム 

本番は障害物認識の精度が悪かったためpsdセンサが使われた 

## 概要

1. カメラで画像を撮る
1. HSV色空間で特定の幅にある画素だけ取り出す
1. 輪郭検出して塊にわける
1. 塊の重心や面積からクラスタリング(k近傍法)

### おまけ

ブラウザでパラメータを変えてどの色が取り出されるか視覚的に調節できるように

外部からアクセスするのだとレスポンスが遅くて使い物になりません

![demo](https://github.com/KoyamaSohei/clustering-ball-and-box/blob/master/screen.gif)

## 必要なもの(ハード)

- raspberrypi 3 model b
- raspberrypi camera

## 必要なもの(ソフト)

- raspbian
- nodejs
- python 3

## 環境構築

```
python -m venv env
source env/bin/activate
pip install -r requirements.txt

npm install

```

## 使い方

1. images/ball/class{n} にクラス{n}の画像を入れる(各クラスにカメラから見て同じ座標にあるボールの画像を入れる)

1. config.ini, color.ini を編集

1. モデル作成

``` 
python createBallModel.py
```

1.  テスト

```
python findBallClass.py
>> [1,2] # class1,class2にボールがあった
```

1. おまけ

```
python server.py
```

localhost:8000 にアクセス