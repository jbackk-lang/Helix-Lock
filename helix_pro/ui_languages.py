"""Regional language registry for the desktop interface.

Regions organize the selector; they never restrict which language may be used.
Untranslated messages fall back to English. A language appearing in the menu
is not a claim that a complete translation exists.
"""

LANGUAGE_REGIONS = {
    "Europa": {
        "pl": "Polski", "en": "English", "de": "Deutsch",
        "fr": "Français", "es": "Español", "it": "Italiano",
        "pt": "Português", "uk": "Українська",
    },
    "Ameryka": {
        "en-US": "English (US)", "es-419": "Español (Latinoamérica)",
        "pt-BR": "Português (Brasil)",
    },
    "Azja": {
        "zh-CN": "简体中文", "ja": "日本語", "ko": "한국어",
        "hi": "हिन्दी", "id": "Bahasa Indonesia",
        "vi": "Tiếng Việt", "th": "ไทย",
    },
}
LANGUAGE_NAMES = {
    code: name for languages in LANGUAGE_REGIONS.values()
    for code, name in languages.items()
}
# Translation catalogs are deliberately separate from available language codes.
# Populate each catalog with reviewed strings before marking a locale complete.
CATALOGS = {"en": {}, "pl": {}}

# Initial translations for common controls and validation messages.
# Remaining strings deliberately fall back to English pending review.
CATALOGS.update({
    "de": {
        "Help / Glossary": "Hilfe / Glossar",
        "Security overview": "Sicherheitsübersicht",
        "Files": "Dateien",
        "Key fingerprint": "Schlüsselfingerabdruck",
        "Password": "Passwort",
        "Key file": "Schlüsseldatei",
        "Source file": "Quelldatei",
        "Browse…": "Durchsuchen…",
        "🔒  Encrypt": "🔒  Verschlüsseln",
        "🔓  Decrypt": "🔓  Entschlüsseln",
        "Close": "Schließen",
        "Important": "Wichtig",
        "QUICK START": "Schnellstart",
        "FILES": "DATEIEN",
        "FILE FORMATS": "DATEIFORMATE",
        "SECURITY": "SICHERHEIT",
        "IMPORTANT": "WICHTIG",
        "Enter a password.": "Passwort eingeben.",
        "Select a key file.": "Schlüsseldatei auswählen.",
        "Key must be exactly 32 bytes.": "Schlüssel muss genau 32 Byte lang sein."
    },
    "fr": {
        "Help / Glossary": "Aide / Glossaire",
        "Security overview": "Vue d’ensemble de la sécurité",
        "Files": "Fichiers",
        "Key fingerprint": "Empreinte de clé",
        "Password": "Mot de passe",
        "Key file": "Fichier de clé",
        "Source file": "Fichier source",
        "Browse…": "Parcourir…",
        "🔒  Encrypt": "🔒  Chiffrer",
        "🔓  Decrypt": "🔓  Déchiffrer",
        "Close": "Fermer",
        "Important": "Important",
        "QUICK START": "Démarrage rapide",
        "FILES": "FICHIERS",
        "FILE FORMATS": "FORMATS DE FICHIERS",
        "SECURITY": "SÉCURITÉ",
        "IMPORTANT": "IMPORTANT",
        "Enter a password.": "Saisissez un mot de passe.",
        "Select a key file.": "Sélectionnez un fichier de clé.",
        "Key must be exactly 32 bytes.": "La clé doit contenir exactement 32 octets."
    },
    "es": {
        "Help / Glossary": "Ayuda / Glosario",
        "Security overview": "Resumen de seguridad",
        "Files": "Archivos",
        "Key fingerprint": "Huella de clave",
        "Password": "Contraseña",
        "Key file": "Archivo de clave",
        "Source file": "Archivo de origen",
        "Browse…": "Examinar…",
        "🔒  Encrypt": "🔒  Cifrar",
        "🔓  Decrypt": "🔓  Descifrar",
        "Close": "Cerrar",
        "Important": "Importante",
        "QUICK START": "Inicio rápido",
        "FILES": "ARCHIVOS",
        "FILE FORMATS": "FORMATOS DE ARCHIVO",
        "SECURITY": "SEGURIDAD",
        "IMPORTANT": "IMPORTANTE",
        "Enter a password.": "Introduce una contraseña.",
        "Select a key file.": "Selecciona un archivo de clave.",
        "Key must be exactly 32 bytes.": "La clave debe tener exactamente 32 bytes."
    },
    "it": {
        "Help / Glossary": "Guida / Glossario",
        "Security overview": "Panoramica della sicurezza",
        "Files": "File",
        "Key fingerprint": "Impronta della chiave",
        "Password": "Password",
        "Key file": "File della chiave",
        "Source file": "File sorgente",
        "Browse…": "Sfoglia…",
        "🔒  Encrypt": "🔒  Cifra",
        "🔓  Decrypt": "🔓  Decifra",
        "Close": "Chiudi",
        "Important": "Importante",
        "QUICK START": "Avvio rapido",
        "FILES": "FILE",
        "FILE FORMATS": "FORMATI DI FILE",
        "SECURITY": "SICUREZZA",
        "IMPORTANT": "IMPORTANTE",
        "Enter a password.": "Inserisci una password.",
        "Select a key file.": "Seleziona un file della chiave.",
        "Key must be exactly 32 bytes.": "La chiave deve contenere esattamente 32 byte."
    },
    "pt-BR": {
        "Help / Glossary": "Ajuda / Glossário",
        "Security overview": "Visão geral da segurança",
        "Files": "Arquivos",
        "Key fingerprint": "Impressão digital da chave",
        "Password": "Senha",
        "Key file": "Arquivo de chave",
        "Source file": "Arquivo de origem",
        "Browse…": "Procurar…",
        "🔒  Encrypt": "🔒  Criptografar",
        "🔓  Decrypt": "🔓  Descriptografar",
        "Close": "Fechar",
        "Important": "Importante",
        "QUICK START": "Início rápido",
        "FILES": "ARQUIVOS",
        "FILE FORMATS": "FORMATOS DE ARQUIVO",
        "SECURITY": "SEGURANÇA",
        "IMPORTANT": "IMPORTANTE",
        "Enter a password.": "Digite uma senha.",
        "Select a key file.": "Selecione um arquivo de chave.",
        "Key must be exactly 32 bytes.": "A chave deve ter exatamente 32 bytes."
    },
    "ja": {
        "Help / Glossary": "ヘルプ / 用語集",
        "Security overview": "セキュリティ概要",
        "Files": "ファイル",
        "Key fingerprint": "鍵のフィンガープリント",
        "Password": "パスワード",
        "Key file": "鍵ファイル",
        "Source file": "元のファイル",
        "Browse…": "参照…",
        "🔒  Encrypt": "🔒  暗号化",
        "🔓  Decrypt": "🔓  復号",
        "Close": "閉じる",
        "Important": "重要",
        "QUICK START": "クイックスタート",
        "FILES": "ファイル",
        "FILE FORMATS": "ファイル形式",
        "SECURITY": "セキュリティ",
        "IMPORTANT": "重要",
        "Enter a password.": "パスワードを入力してください。",
        "Select a key file.": "鍵ファイルを選択してください。",
        "Key must be exactly 32 bytes.": "鍵は正確に32バイトである必要があります。"
    },
    "zh-CN": {
        "Help / Glossary": "帮助 / 术语表",
        "Security overview": "安全概览",
        "Files": "文件",
        "Key fingerprint": "密钥指纹",
        "Password": "密码",
        "Key file": "密钥文件",
        "Source file": "源文件",
        "Browse…": "浏览…",
        "🔒  Encrypt": "🔒  加密",
        "🔓  Decrypt": "🔓  解密",
        "Close": "关闭",
        "Important": "重要",
        "QUICK START": "快速入门",
        "FILES": "文件",
        "FILE FORMATS": "文件格式",
        "SECURITY": "安全",
        "IMPORTANT": "重要",
        "Enter a password.": "请输入密码。",
        "Select a key file.": "请选择密钥文件。",
        "Key must be exactly 32 bytes.": "密钥必须恰好为32字节。"
    },
    "ko": {
        "Help / Glossary": "도움말 / 용어집",
        "Security overview": "보안 개요",
        "Files": "파일",
        "Key fingerprint": "키 지문",
        "Password": "비밀번호",
        "Key file": "키 파일",
        "Source file": "원본 파일",
        "Browse…": "찾아보기…",
        "🔒  Encrypt": "🔒  암호화",
        "🔓  Decrypt": "🔓  복호화",
        "Close": "닫기",
        "Important": "중요",
        "QUICK START": "빠른 시작",
        "FILES": "파일",
        "FILE FORMATS": "파일 형식",
        "SECURITY": "보안",
        "IMPORTANT": "중요",
        "Enter a password.": "비밀번호를 입력하세요.",
        "Select a key file.": "키 파일을 선택하세요.",
        "Key must be exactly 32 bytes.": "키는 정확히 32바이트여야 합니다."
    }
})

# Additional initial locale coverage; other messages fall back to English.
CATALOGS.update({
    "pt": {
        "Help / Glossary": "Ajuda / Glossário",
        "Security overview": "Visão geral da segurança",
        "Files": "Ficheiros",
        "Key fingerprint": "Impressão digital da chave",
        "Password": "Palavra-passe",
        "Key file": "Ficheiro de chave",
        "Source file": "Ficheiro de origem",
        "Browse…": "Procurar…",
        "🔒  Encrypt": "🔒  Encriptar",
        "🔓  Decrypt": "🔓  Desencriptar",
        "Close": "Fechar",
        "Important": "Importante",
        "QUICK START": "INÍCIO RÁPIDO",
        "FILES": "FICHEIROS",
        "FILE FORMATS": "FORMATOS DE FICHEIRO",
        "SECURITY": "SEGURANÇA",
        "IMPORTANT": "IMPORTANTE",
        "Enter a password.": "Introduza uma palavra-passe.",
        "Select a key file.": "Selecione um ficheiro de chave.",
        "Key must be exactly 32 bytes.": "A chave deve ter exatamente 32 bytes."
    },
    "uk": {
        "Help / Glossary": "Довідка / Глосарій",
        "Security overview": "Огляд безпеки",
        "Files": "Файли",
        "Key fingerprint": "Відбиток ключа",
        "Password": "Пароль",
        "Key file": "Файл ключа",
        "Source file": "Вихідний файл",
        "Browse…": "Огляд…",
        "🔒  Encrypt": "🔒  Зашифрувати",
        "🔓  Decrypt": "🔓  Розшифрувати",
        "Close": "Закрити",
        "Important": "Важливо",
        "QUICK START": "ШВИДКИЙ ПОЧАТОК",
        "FILES": "ФАЙЛИ",
        "FILE FORMATS": "ФОРМАТИ ФАЙЛІВ",
        "SECURITY": "БЕЗПЕКА",
        "IMPORTANT": "ВАЖЛИВО",
        "Enter a password.": "Введіть пароль.",
        "Select a key file.": "Виберіть файл ключа.",
        "Key must be exactly 32 bytes.": "Ключ повинен містити рівно 32 байти."
    },
    "hi": {
        "Help / Glossary": "सहायता / शब्दावली",
        "Security overview": "सुरक्षा अवलोकन",
        "Files": "फ़ाइलें",
        "Key fingerprint": "कुंजी फ़िंगरप्रिंट",
        "Password": "पासवर्ड",
        "Key file": "कुंजी फ़ाइल",
        "Source file": "स्रोत फ़ाइल",
        "Browse…": "ब्राउज़ करें…",
        "🔒  Encrypt": "🔒  एन्क्रिप्ट करें",
        "🔓  Decrypt": "🔓  डिक्रिप्ट करें",
        "Close": "बंद करें",
        "Important": "महत्वपूर्ण",
        "QUICK START": "त्वरित शुरुआत",
        "FILES": "फ़ाइलें",
        "FILE FORMATS": "फ़ाइल प्रारूप",
        "SECURITY": "सुरक्षा",
        "IMPORTANT": "महत्वपूर्ण",
        "Enter a password.": "पासवर्ड दर्ज करें।",
        "Select a key file.": "कुंजी फ़ाइल चुनें।",
        "Key must be exactly 32 bytes.": "कुंजी ठीक 32 बाइट की होनी चाहिए।"
    },
    "id": {
        "Help / Glossary": "Bantuan / Glosarium",
        "Security overview": "Ringkasan keamanan",
        "Files": "Berkas",
        "Key fingerprint": "Sidik jari kunci",
        "Password": "Kata sandi",
        "Key file": "Berkas kunci",
        "Source file": "Berkas sumber",
        "Browse…": "Telusuri…",
        "🔒  Encrypt": "🔒  Enkripsi",
        "🔓  Decrypt": "🔓  Dekripsi",
        "Close": "Tutup",
        "Important": "Penting",
        "QUICK START": "MULAI CEPAT",
        "FILES": "BERKAS",
        "FILE FORMATS": "FORMAT BERKAS",
        "SECURITY": "KEAMANAN",
        "IMPORTANT": "PENTING",
        "Enter a password.": "Masukkan kata sandi.",
        "Select a key file.": "Pilih berkas kunci.",
        "Key must be exactly 32 bytes.": "Kunci harus tepat 32 byte."
    },
    "vi": {
        "Help / Glossary": "Trợ giúp / Thuật ngữ",
        "Security overview": "Tổng quan bảo mật",
        "Files": "Tệp",
        "Key fingerprint": "Dấu vân tay khóa",
        "Password": "Mật khẩu",
        "Key file": "Tệp khóa",
        "Source file": "Tệp nguồn",
        "Browse…": "Duyệt…",
        "🔒  Encrypt": "🔒  Mã hóa",
        "🔓  Decrypt": "🔓  Giải mã",
        "Close": "Đóng",
        "Important": "Quan trọng",
        "QUICK START": "BẮT ĐẦU NHANH",
        "FILES": "TỆP",
        "FILE FORMATS": "ĐỊNH DẠNG TỆP",
        "SECURITY": "BẢO MẬT",
        "IMPORTANT": "QUAN TRỌNG",
        "Enter a password.": "Nhập mật khẩu.",
        "Select a key file.": "Chọn tệp khóa.",
        "Key must be exactly 32 bytes.": "Khóa phải có đúng 32 byte."
    },
    "th": {
        "Help / Glossary": "วิธีใช้ / อภิธานศัพท์",
        "Security overview": "ภาพรวมความปลอดภัย",
        "Files": "ไฟล์",
        "Key fingerprint": "ลายนิ้วมือกุญแจ",
        "Password": "รหัสผ่าน",
        "Key file": "ไฟล์กุญแจ",
        "Source file": "ไฟล์ต้นฉบับ",
        "Browse…": "เรียกดู…",
        "🔒  Encrypt": "🔒  เข้ารหัส",
        "🔓  Decrypt": "🔓  ถอดรหัส",
        "Close": "ปิด",
        "Important": "สำคัญ",
        "QUICK START": "เริ่มต้นอย่างรวดเร็ว",
        "FILES": "ไฟล์",
        "FILE FORMATS": "รูปแบบไฟล์",
        "SECURITY": "ความปลอดภัย",
        "IMPORTANT": "สำคัญ",
        "Enter a password.": "ป้อนรหัสผ่าน",
        "Select a key file.": "เลือกไฟล์กุญแจ",
        "Key must be exactly 32 bytes.": "กุญแจต้องมีขนาด 32 ไบต์พอดี"
    }
})

# Safety-critical notices and file-operation labels; pending native-speaker review.
CATALOGS.update({
    "de": {
        "Operation complete": "Vorgang abgeschlossen",
        "Operation failed": "Vorgang fehlgeschlagen",
        "Confirm overwrite": "Überschreiben bestätigen",
        "Select an existing file.": "Vorhandene Datei auswählen.",
        "Encryption": "Verschlüsselung",
        "Decryption": "Entschlüsselung",
        "Save encrypted file": "Verschlüsselte Datei speichern",
        "Save decrypted file": "Entschlüsselte Datei speichern",
        "Save new key": "Neuen Schlüssel speichern",
        "Key generated. Store a secure backup away from this device.": "Schlüssel erstellt. Bewahren Sie eine sichere Kopie außerhalb dieses Geräts auf.",
        "Choose another name. Existing key was not overwritten.": "Anderen Namen wählen. Der vorhandene Schlüssel wurde nicht überschrieben.",
        "Losing the key or password may make recovery impossible.": "Schlüssel oder Passwortverlust kann die Wiederherstellung unmöglich machen.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lock ist Beta-Software und wurde keiner unabhängigen Sicherheitsprüfung unterzogen."
    },
    "fr": {
        "Operation complete": "Opération terminée",
        "Operation failed": "Échec de l’opération",
        "Confirm overwrite": "Confirmer l’écrasement",
        "Select an existing file.": "Sélectionnez un fichier existant.",
        "Encryption": "Chiffrement",
        "Decryption": "Déchiffrement",
        "Save encrypted file": "Enregistrer le fichier chiffré",
        "Save decrypted file": "Enregistrer le fichier déchiffré",
        "Save new key": "Enregistrer la nouvelle clé",
        "Key generated. Store a secure backup away from this device.": "Clé générée. Conservez une copie sécurisée hors de cet appareil.",
        "Choose another name. Existing key was not overwritten.": "Choisissez un autre nom. La clé existante n’a pas été écrasée.",
        "Losing the key or password may make recovery impossible.": "La perte de la clé ou du mot de passe peut rendre la récupération impossible.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lock est un logiciel bêta qui n’a pas fait l’objet d’un audit de sécurité indépendant."
    },
    "es": {
        "Operation complete": "Operación completada",
        "Operation failed": "Error en la operación",
        "Confirm overwrite": "Confirmar sobrescritura",
        "Select an existing file.": "Selecciona un archivo existente.",
        "Encryption": "Cifrado",
        "Decryption": "Descifrado",
        "Save encrypted file": "Guardar archivo cifrado",
        "Save decrypted file": "Guardar archivo descifrado",
        "Save new key": "Guardar nueva clave",
        "Key generated. Store a secure backup away from this device.": "Clave generada. Guarda una copia segura fuera de este dispositivo.",
        "Choose another name. Existing key was not overwritten.": "Elige otro nombre. La clave existente no se ha sobrescrito.",
        "Losing the key or password may make recovery impossible.": "Perder la clave o la contraseña puede impedir la recuperación.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lock es software beta y no se ha sometido a una auditoría de seguridad independiente."
    },
    "it": {
        "Operation complete": "Operazione completata",
        "Operation failed": "Operazione non riuscita",
        "Confirm overwrite": "Conferma sovrascrittura",
        "Select an existing file.": "Seleziona un file esistente.",
        "Encryption": "Cifratura",
        "Decryption": "Decifratura",
        "Save encrypted file": "Salva file cifrato",
        "Save decrypted file": "Salva file decifrato",
        "Save new key": "Salva nuova chiave",
        "Key generated. Store a secure backup away from this device.": "Chiave generata. Conserva una copia sicura fuori da questo dispositivo.",
        "Choose another name. Existing key was not overwritten.": "Scegli un altro nome. La chiave esistente non è stata sovrascritta.",
        "Losing the key or password may make recovery impossible.": "La perdita della chiave o della password può rendere impossibile il recupero.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lock è un software beta e non è stato sottoposto a una verifica di sicurezza indipendente."
    },
    "pt": {
        "Operation complete": "Operação concluída",
        "Operation failed": "Falha na operação",
        "Confirm overwrite": "Confirmar substituição",
        "Select an existing file.": "Selecione um ficheiro existente.",
        "Encryption": "Encriptação",
        "Decryption": "Desencriptação",
        "Save encrypted file": "Guardar ficheiro encriptado",
        "Save decrypted file": "Guardar ficheiro desencriptado",
        "Save new key": "Guardar nova chave",
        "Key generated. Store a secure backup away from this device.": "Chave gerada. Guarde uma cópia segura fora deste dispositivo.",
        "Choose another name. Existing key was not overwritten.": "Escolha outro nome. A chave existente não foi substituída.",
        "Losing the key or password may make recovery impossible.": "A perda da chave ou palavra-passe pode impossibilitar a recuperação.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "O Helix-Lock é software beta e não foi sujeito a uma auditoria de segurança independente."
    },
    "pt-BR": {
        "Operation complete": "Operação concluída",
        "Operation failed": "Falha na operação",
        "Confirm overwrite": "Confirmar substituição",
        "Select an existing file.": "Selecione um arquivo existente.",
        "Encryption": "Criptografia",
        "Decryption": "Descriptografia",
        "Save encrypted file": "Salvar arquivo criptografado",
        "Save decrypted file": "Salvar arquivo descriptografado",
        "Save new key": "Salvar nova chave",
        "Key generated. Store a secure backup away from this device.": "Chave gerada. Guarde uma cópia segura fora deste dispositivo.",
        "Choose another name. Existing key was not overwritten.": "Escolha outro nome. A chave existente não foi substituída.",
        "Losing the key or password may make recovery impossible.": "A perda da chave ou senha pode impossibilitar a recuperação.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "O Helix-Lock é um software beta e não passou por uma auditoria de segurança independente."
    },
    "uk": {
        "Operation complete": "Операцію завершено",
        "Operation failed": "Помилка операції",
        "Confirm overwrite": "Підтвердити перезапис",
        "Select an existing file.": "Виберіть наявний файл.",
        "Encryption": "Шифрування",
        "Decryption": "Розшифрування",
        "Save encrypted file": "Зберегти зашифрований файл",
        "Save decrypted file": "Зберегти розшифрований файл",
        "Save new key": "Зберегти новий ключ",
        "Key generated. Store a secure backup away from this device.": "Ключ створено. Збережіть захищену резервну копію поза цим пристроєм.",
        "Choose another name. Existing key was not overwritten.": "Виберіть іншу назву. Наявний ключ не перезаписано.",
        "Losing the key or password may make recovery impossible.": "Втрата ключа або пароля може унеможливити відновлення.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lock — бета-версія, яка не проходила незалежний аудит безпеки."
    },
    "ja": {
        "Operation complete": "操作が完了しました",
        "Operation failed": "操作に失敗しました",
        "Confirm overwrite": "上書きの確認",
        "Select an existing file.": "既存のファイルを選択してください。",
        "Encryption": "暗号化",
        "Decryption": "復号",
        "Save encrypted file": "暗号化ファイルを保存",
        "Save decrypted file": "復号したファイルを保存",
        "Save new key": "新しい鍵を保存",
        "Key generated. Store a secure backup away from this device.": "鍵を生成しました。この端末とは別の場所に安全なバックアップを保管してください。",
        "Choose another name. Existing key was not overwritten.": "別の名前を選択してください。既存の鍵は上書きされていません。",
        "Losing the key or password may make recovery impossible.": "鍵やパスワードを失うと、データを復元できなくなる可能性があります。",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lockはベータ版であり、独立したセキュリティ監査を受けていません。"
    },
    "zh-CN": {
        "Operation complete": "操作完成",
        "Operation failed": "操作失败",
        "Confirm overwrite": "确认覆盖",
        "Select an existing file.": "请选择现有文件。",
        "Encryption": "加密",
        "Decryption": "解密",
        "Save encrypted file": "保存加密文件",
        "Save decrypted file": "保存解密文件",
        "Save new key": "保存新密钥",
        "Key generated. Store a secure backup away from this device.": "密钥已生成。请在此设备之外安全备份。",
        "Choose another name. Existing key was not overwritten.": "请选择其他名称。现有密钥未被覆盖。",
        "Losing the key or password may make recovery impossible.": "丢失密钥或密码可能导致无法恢复数据。",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lock 仍处于测试阶段，尚未经过独立安全审计。"
    },
    "ko": {
        "Operation complete": "작업 완료",
        "Operation failed": "작업 실패",
        "Confirm overwrite": "덮어쓰기 확인",
        "Select an existing file.": "기존 파일을 선택하세요.",
        "Encryption": "암호화",
        "Decryption": "복호화",
        "Save encrypted file": "암호화된 파일 저장",
        "Save decrypted file": "복호화된 파일 저장",
        "Save new key": "새 키 저장",
        "Key generated. Store a secure backup away from this device.": "키가 생성되었습니다. 이 장치 외부에 안전한 백업을 보관하세요.",
        "Choose another name. Existing key was not overwritten.": "다른 이름을 선택하세요. 기존 키는 덮어쓰지 않았습니다.",
        "Losing the key or password may make recovery impossible.": "키나 비밀번호를 분실하면 데이터를 복구하지 못할 수 있습니다.",
        "Helix-Lock is beta software and has not undergone an independent security audit.": "Helix-Lock은 베타 소프트웨어이며 독립적인 보안 감사를 받지 않았습니다."
    }
})

LANGUAGE_FALLBACKS = {"en-US": "en", "es-419": "es", "pt-BR": "pt"}


def region_for_language(language: str) -> str:
    for region, languages in LANGUAGE_REGIONS.items():
        if language in languages:
            return region
    return "Europa"


def translate(language: str, english: str, polish: str = "") -> str:
    """Return reviewed translation or English fallback; never join languages."""
    if language == "pl":
        return CATALOGS["pl"].get(english, polish or english)
    catalog = CATALOGS.get(language, {})
    if english in catalog:
        return catalog[english]
    base = LANGUAGE_FALLBACKS.get(language)
    if base and english in CATALOGS.get(base, {}):
        return CATALOGS[base][english]
    return english
