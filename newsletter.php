<?php
// Newsletter sign-up: stores the address outside the web root and notifies the studio inbox.
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function out($ok, $code = 200) { http_response_code($code); echo json_encode(['ok' => $ok]); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(false, 405);
if (!empty($_POST['_honey'])) out(true);

$email = trim(str_replace(["\r", "\n", "\0"], '', (string)($_POST['email'] ?? '')));
$lang  = ($_POST['lang'] ?? '') === 'en' ? 'en' : 'pl';
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || empty($_POST['consent'])) out(false, 422);

$saved = false;
$dir = dirname(__DIR__) . '/newsletter-data';
if (is_dir($dir) || @mkdir($dir, 0700, true)) {
  $line = [date('c'), $email, $lang, 'zgoda: tak'];
  $fh = @fopen($dir . '/subskrybenci.csv', 'a');
  if ($fh) { $saved = fputcsv($fh, $line) !== false; fclose($fh); }
}

$subject = '=?UTF-8?B?' . base64_encode('Nowy zapis do newslettera: ' . $email) . '?=';
$body = "Nowa osoba zapisała się do newslettera na stankiewicz.design.\n\nE-mail: $email\nJęzyk strony: $lang\nData: " . date('Y-m-d H:i') . "\nZgoda na wiadomości: tak\n";
$headers = implode("\r\n", [
  'From: Stankiewicz Design <formularz@stankiewicz.design>',
  'Reply-To: ' . $email,
  'MIME-Version: 1.0',
  'Content-Type: text/plain; charset=UTF-8',
]);
$mailed = mail('d.stankiewicz.design@gmail.com', $subject, $body, $headers, '-fformularz@stankiewicz.design');

out($saved || $mailed);
