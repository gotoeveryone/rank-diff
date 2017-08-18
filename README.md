# 段位別差分抽出バッチ #

## 概要

所属国（組織）単位で段位の差分を抽出します。

## 前提

以下がインストールされていること。

- Python2.x

## セットアップ

```sh
$ # virtualenvの設定
$ pip install virtualenv
$ virtualenv -p <python_path> ./venv
$
$ # パッケージの取得
$ pip install -r requirements.txt
$
$ # 以下はOSによって異なります。
$ # UNIX系
$ . ./venv/bin/activate
$ # Windows
$ . .\venv\Scripts\activate
```

## 実行

1. ルートディレクトリの`.env.example`を`.env`にコピーし、環境に合わせて修正してください。
2. 以下コマンドを実行してください。

```sh
$ python main.py
```
