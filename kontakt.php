<?php
// Contact form endpoint: sends the brief to the studio inbox via the hosting's mail().
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

function out($ok, $code = 200) { http_response_code($code); echo json_encode(['ok' => $ok]); exit; }
function clean($v, $max) { return trim(mb_substr(str_replace(["\r", "\0"], '', (string)$v), 0, $max)); }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(false, 405);
if (!empty($_POST['_honey'])) out(true); // bot filled the hidden field: pretend success

$name  = clean($_POST['name'] ?? '', 120);
$email = clean($_POST['email'] ?? '', 200);
$type  = clean($_POST['type'] ?? '', 120);
$msg   = clean($_POST['message'] ?? '', 5000);
if ($name === '' || $msg === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) out(false, 422);

$to      = 'd.stankiewicz.design@gmail.com';
$subject = '=?UTF-8?B?' . base64_encode('Nowe zapytanie ze strony: ' . str_replace("\n", ' ', $name)) . '?=';
$body    = "Imię: $name\nE-mail: $email\nTyp projektu: $type\n\n$msg\n\n— wysłane z formularza na stankiewicz.design\n";
$headers = implode("\r\n", [
  'From: Stankiewicz Design <formularz@stankiewicz.design>',
  'Reply-To: ' . str_replace("\n", '', $email),
  'MIME-Version: 1.0',
  'Content-Type: text/plain; charset=UTF-8',
  'Content-Transfer-Encoding: 8bit',
]);

out(mail($to, $subject, $body, $headers, '-fformularz@stankiewicz.design'), 200);
