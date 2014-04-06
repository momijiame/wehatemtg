wehatemtg
=========

We hate meeting

# これは何？

会議で浪費される人件費を表示するためのアプリケーションです。
メンバーの年収や参加人数などを入力すると、会議でこれまでに使われた人件費の概算値が分かります。

# 名前の由来

みんな会議は嫌いですよね。

# インストール

インストールと実行には Python が必要です。

## GitHub のソースコードからインストールする

```
$ git clone https://github.com/momijiame/wehatemtg.git
$ cd wehatemtg
$ python setup.py install
```

## PIP でインストールする

```
$ pip install git+https://github.com/momijiame/wehatemtg.git
```

# 使い方

wehatemtg をインストールすると mtg コマンドが使えるようになります。
会議が始まったら mtg コマンドを実行しましょう。

例えばオプションを一切指定しない場合には、サラリーマンの平均年収と労働時間を元に 1 人が消費する人件費を表示し続けます。
労働時間のデフォルト値はかなりホワイトに設定してありますし、1 人でやるミーティングもないでしょうから、オプションは適宜変更しましょう。

```
$ mtg
```

# TODO

X 分前から始まった会議も表示できるようにする
