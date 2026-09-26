/**
 * Googleドライブのフォルダ内の画像を、Googleドキュメントの無料OCRで一括文字起こしする（Google Apps Script）
 *
 * 【初回の設定】
 *  1. Googleドライブに画像用のフォルダを作り、画像を入れる（001.png, 002.png … の連番にすると並び順が崩れない）
 *  2. フォルダを開いたときのURL末尾（https://drive.google.com/drive/folders/XXXX の XXXX）を下の FOLDER_ID に貼る
 *  3. https://script.google.com →「新しいプロジェクト」→ このファイルの中身を全部貼り付けて保存
 *  4. 左の「サービス」の「＋」→「Drive API」を選んで「追加」
 *  5. 上の関数選択で runOcr を選び「実行」→ 初回だけGoogleアカウントの許可を求められるので許可する
 *
 * 【結果】画像フォルダの中に「OCR結果」フォルダができ、次のファイルが作られる
 *  <画像名>.txt        … 画像ごとの結果
 *  <画像名>.error.txt  … 失敗した画像（このファイルを削除して runOcr を再実行すると、その画像だけやり直す）
 *  all.txt             … 全画像の結果をファイル名順につないだもの（全部終わったときに作られる）
 *
 * 【200枚以上でも大丈夫な理由】Apps Script は1回6分までしか動けないため、5分たったら自動で1分後に続きを予約して止まる。
 *  全部終わるまでブラウザを閉じてよい。進み具合は「OCR結果」フォルダの .txt の数で分かる。
 *  2回目以降は、画像を足して runOcr を実行するだけでよい（結果が既にある画像は飛ばす）。
 */

const FOLDER_ID = 'ここにフォルダIDを貼る';
const OCR_LANG = 'ja';                 // 読み取る言語（英語だけの画像なら 'en'）
const TIME_LIMIT_MS = 5 * 60 * 1000;   // 6分制限の手前で止めて続きを予約する
const OUT_NAME = 'OCR結果';

function runOcr() {
  const start = Date.now();
  deleteTriggers_();
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const out = getOrCreateFolder_(folder, OUT_NAME);

  const existing = new Set();
  const outFiles = out.getFiles();
  while (outFiles.hasNext()) existing.add(outFiles.next().getName());

  const images = listImages_(folder);
  let processed = 0;
  for (const img of images) {
    const base = baseName_(img.getName());
    if (existing.has(base + '.txt') || existing.has(base + '.error.txt')) continue;
    if (Date.now() - start > TIME_LIMIT_MS) {
      ScriptApp.newTrigger('runOcr').timeBased().after(60 * 1000).create();
      console.log(`今回 ${processed} 枚処理。1分後に続きを自動で実行します。`);
      return;
    }
    try {
      out.createFile(base + '.txt', ocr_(img, out), MimeType.PLAIN_TEXT);
    } catch (e) {
      out.createFile(base + '.error.txt', String(e), MimeType.PLAIN_TEXT);
      console.log(`失敗: ${img.getName()} ${e}`);
    }
    processed++;
  }
  writeAll_(images, out);
  console.log(`完了: ${images.length} 枚。「${OUT_NAME}」フォルダの all.txt を確認してください。`);
}

// 画像を一時的にGoogleドキュメントへ変換（＝OCR）し、文字だけを取り出して一時ファイルは削除する
function ocr_(img, out) {
  const doc = Drive.Files.create(
    { name: img.getName(), mimeType: MimeType.GOOGLE_DOCS, parents: [out.getId()] },
    img.getBlob(),
    { ocrLanguage: OCR_LANG }
  );
  try {
    const text = DocumentApp.openById(doc.id).getBody().getText().trim();
    return text || '（文字なし）';
  } finally {
    DriveApp.getFileById(doc.id).setTrashed(true);
  }
}

function listImages_(folder) {
  const images = [];
  const files = folder.getFiles();
  while (files.hasNext()) {
    const f = files.next();
    if (f.getMimeType().indexOf('image/') === 0) images.push(f);
  }
  // 1, 2, 10 の順になるよう数字を数値として比べる
  return images.sort((a, b) => a.getName().localeCompare(b.getName(), 'ja', { numeric: true }));
}

function writeAll_(images, out) {
  const parts = images.map(img => {
    const base = baseName_(img.getName());
    const f = out.getFilesByName(base + '.txt');
    const body = f.hasNext() ? f.next().getBlob().getDataAsString('UTF-8').trim() : '（失敗: ' + base + '.error.txt を参照）';
    return `## ${img.getName()}\n\n${body}\n`;
  });
  const old = out.getFilesByName('all.txt');
  while (old.hasNext()) old.next().setTrashed(true);
  out.createFile('all.txt', parts.join('\n'), MimeType.PLAIN_TEXT);
}

function getOrCreateFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : parent.createFolder(name);
}

function baseName_(name) {
  return name.replace(/\.[^.]+$/, '');
}

function deleteTriggers_() {
  for (const t of ScriptApp.getProjectTriggers()) {
    if (t.getHandlerFunction() === 'runOcr') ScriptApp.deleteTrigger(t);
  }
}
