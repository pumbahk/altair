# famic-bench - famiport api performance test

## 環境

### 必要なパッケージ

- funkload
- konbu
- lxml
- zope.interface
- zope.component
- famic (これはpypiにはありませんがaltairリポジトリ内にあります)

## 準備

### FamiPort用の予約を作成する

cartbotで作成すると簡単でしょう。実際にテストで処理する数より多くの予約を作成してください。

### FamiPortReceipt.reserve_number の一覧を reserve_number.txt に出力する

`reserve_number.txt` に `FamiPortReceipt.reserve_number` の一覧を出力しておく必要があります。
テストではその一覧のデータを使ってAPIをcallするからです。
以下の例では全てのFamiPortReceiptを対象にしています。

```
$ echo "SELECT FamiPortReceipt.reserve_number FROM FamiPortReceipt;" | mysql -u root -D famiport > reserve_number.txt
```

## 実行確認

テストが実行できるかどうかを確認します。

```
$ fl-run-test -dv test_Simple.py
```

## 実行方法

以下の場合cuncurrencyが1, 25, 50, 75のパターンでテストを実施します。

```
$ fl-run-bench -c 1:25:50:75 test_Simple.py Simple.test_it
```

## レポート

HTMLとしてレポートを出力します。

```
$ fl-build-report --html simple-bench.xml
```
