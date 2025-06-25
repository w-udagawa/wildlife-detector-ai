# Wildlife Detector AI v2.0 - 環境問題の解決策

## 判明した問題

Pythonパスの出力から、miniforge3のPythonが仮想環境より優先されていることが判明しました：

```
C:\Users\AU3009\AppData\Local\miniforge3\python312.zip
C:\Users\AU3009\AppData\Local\miniforge3\DLLs
C:\Users\AU3009\AppData\Local\miniforge3\Lib
C:\Users\AU3009\AppData\Local\miniforge3
C:\Users\AU3009\Claudeworks\projects\wildlife-detector\venv
```

これにより、JSONモジュールがminiforge3から読み込まれ、SpeciesNetとの互換性問題が発生しています。

## 実装した解決策

1. **環境変数のクリーンアップ**
   - miniforge3をPATHから除外
   - 仮想環境のパスを最優先に設定
   - PYTHONHOME、PYTHONPATHを削除

2. **Python実行環境の明示的指定**
   - 仮想環境のpython.exeを直接使用

## テスト手順

### 1. クリーン環境でのテスト
```
test_clean_env.bat
```

### 2. SpeciesNetパラメータの確認
```
venv\Scripts\activate
python check_speciesnet_params.py
```

### 3. 修正後のCLIテスト
```
test_cli.bat
```

## 代替案（問題が解決しない場合）

### オプション1: 手動でSpeciesNetを実行してから解析
```python
# 1. まずSpeciesNetを直接実行
os.system(f'"{venv_python}" -m speciesnet.scripts.run_model ...')

# 2. 生成されたJSONファイルを読み込む
with open(output_file, 'r') as f:
    results = json.load(f)
```

### オプション2: 一時的にMOCKモードを使用
```python
# config.yamlを編集
detection:
  model_name: mock  # speciesnetの代わりに
```

### オプション3: SpeciesNetの再インストール
```batch
venv\Scripts\activate
pip uninstall speciesnet -y
pip install speciesnet==5.0.0
```

## 確認事項

1. test_crow.batは正常に動作していますか？
2. output/crow_result.jsonは正しく生成されていますか？
3. miniforge3を使用する他のアプリケーションはありますか？

これらの情報を確認した上で、さらなる対策を検討します。
