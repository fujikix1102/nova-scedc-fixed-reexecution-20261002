# CosmoSIS再現性Runner

`cosmosis_repro_runner.py` は、固定したCosmoSISリポジトリに対して、バージョン確認、標準E2E、回帰テスト、実行Manifest、SHA256SUMSを一括生成します。

## 実行例

```text
PATH=/path/to/python311/bin:$PATH \
python tools/cosmosis_repro_runner.py \
  --repo /path/to/cosmosis \
  --output /path/to/output/cosmosis_repro
```

回帰テストを省略する場合は `--skip-tests` を指定します。E2Eの終了コード、回帰テストの終了コード、コミット、出力SHAをManifestへ保存します。形式検証の合格を意味しないため、`formal_pass` は常に `false` です。
