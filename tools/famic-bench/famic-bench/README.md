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



This is a famiport api performance test.

It requires an famiport api server . test server (configuration is done for an apache2
default install)

WARNING: You should *not* run this script against a server that is not under
your responsablity as it can result a DOS in bench mode.

- Modify the Simple.conf file

  Set the [main] url and pages keys

- Test it

   verbose mode::

     fl-run-test -v test_Simple.py

   debug mode::

     fl-run-test -d test_Simple.py

   view the downloaded page in real time using firefox::

     fl-run-test -V test_Simple.py

   check performance of a single page::

     fl-run-test -l 4 -n 100 test_Simple.py


- Bench it

   Start a monitord server to log server activities::

     fl-monitor-ctl monitor.conf start

   Bench it with few cycles::

     fl-run-bench -c 1:25:50:75 test_Simple.py Simple.test_simple

   Note that for correct interpretation you should run the FunkLoad bencher
   in a different host than the server, the server should be 100% dedicated
   to the application.

   If you want to bench with more than 200 users, you need to reduce the
   default stack size used by a thread, for example try a `ulimit -s 2048`
   before running the bench.

   Performance limits are hit by FunkLoad before apache's limit is reached,
   since it uses significant CPU resources.

- Build the report::

   fl-build-report --html simple-bench.xml
