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


def merge_catalogs(translations: dict) -> None:
    """Extend existing locales without discarding earlier translated messages."""
    for locale, messages in translations.items():
        CATALOGS.setdefault(locale, {}).update(messages)


# Initial translations for common controls and validation messages.
# Remaining strings deliberately fall back to English pending review.
merge_catalogs({
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
merge_catalogs({
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
merge_catalogs({
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

# Full offline F1 help: first three additional locales, pending language review.
merge_catalogs({
    "de": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. Wählen Sie auf der Registerkarte Dateien die Quelldatei aus.\n2. Wählen Sie ein Passwort oder eine 32-Byte-Schlüsseldatei.\n3. Klicken Sie auf Verschlüsseln und wählen Sie einen Speicherort; bewahren Sie das Original auf.\n4. Wählen Sie zum Wiederherstellen die verschlüsselte Datei und denselben Schlüssel oder dasselbe Passwort, dann Entschlüsseln.\n5. Prüfen Sie die wiederhergestellte Datei, bevor Sie Sicherungen löschen.\nF1 öffnet diese Hilfe auf jeder Registerkarte.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "Quelldatei: zu verarbeitende Datei.\nSchlüsseldatei: geheime Datei mit 32 Byte.\nPasswort: Alternative zur Schlüsseldatei.\nVerschlüsseln: erstellt eine verschlüsselte Datei.\nEntschlüsseln: stellt Inhalte nach erfolgreicher Authentifizierung wieder her.\nSchlüssel erzeugen: erstellt einen neuen Zufallsschlüssel.\nÜberschreiben: ersetzt eine vorhandene Ausgabedatei.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: grundlegendes Verschlüsselungsformat.\nHLXN: verschlüsselter Container mit ursprünglichem Dateinamen.\nHLXC / CounterLock: Format mit Lesezähler; separate Prüfung des Registers erforderlich.\nHLOB: experimentelle OBX1-Kompression mit AES-GCM.\nHLOM: experimentelles Omega-Format mit begrenzter GF(256)-Reparatur.\nOBX1: nur Kompression — KEINE Verschlüsselung.\nHLOB und HLOM sind keine Standardmodi der Schaltfläche Entschlüsseln.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: experimentelles Register für Schlüsselidentitäten und Ereignisse.\nChain: lokale Konsistenz der Einträge.\nSequence: Anzahl der Ereignisse.\nCheckpoint: erfordert unabhängige Prüfung.\nTrust Anchor: externe Vertrauensreferenz.\nQuorum: erforderliche Mehrheit unabhängiger Zeugen.\nFingerprint: Kennung eines Schlüssels oder Chiffrats, NICHT der geheime Schlüssel.\nDateiformat: Erkennung des Headers, KEIN Echtheitsnachweis.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Bewahren Sie Sicherungen des Schlüssels und der Originaldatei auf einem anderen Gerät auf.\nDer Verlust des Schlüssels oder Passworts kann die Wiederherstellung unmöglich machen.\nHelix-Lock ist Beta-Software und wurde keiner unabhängigen Sicherheitsprüfung unterzogen."
    },
    "es": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. En la pestaña Archivos, selecciona el archivo de origen.\n2. Elige una contraseña o un archivo de clave de 32 bytes.\n3. Pulsa Cifrar y elige dónde guardar el resultado; conserva el original.\n4. Para recuperar los datos, selecciona el archivo cifrado, usa la misma clave o contraseña y pulsa Descifrar.\n5. Comprueba el archivo recuperado antes de borrar las copias de seguridad.\nF1 abre esta ayuda desde cualquier pestaña.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "Archivo de origen: archivo que se procesará.\nArchivo de clave: archivo secreto de 32 bytes.\nContraseña: alternativa al archivo de clave.\nCifrar: crea un archivo cifrado.\nDescifrar: recupera el contenido tras una autenticación correcta.\nGenerar clave: crea una clave aleatoria nueva.\nSobrescribir: sustituye un archivo de salida existente.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: formato básico de cifrado.\nHLXN: contenedor cifrado con el nombre original del archivo.\nHLXC / CounterLock: formato con contador de lecturas; requiere verificar el registro por separado.\nHLOB: compresión experimental OBX1 con AES-GCM.\nHLOM: formato experimental Omega con reparación limitada GF(256).\nOBX1: solo compresión; NO cifra.\nHLOB y HLOM no son modos estándar del botón Descifrar.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: registro experimental de identidades de claves y eventos.\nCadena: coherencia local de las entradas.\nSecuencia: número de eventos.\nPunto de control: requiere verificación independiente.\nAncla de confianza: referencia de confianza externa.\nQuórum: mayoría necesaria de testigos independientes.\nHuella: identificador de una clave o archivo cifrado; NO es la clave secreta.\nFormato: detectar la cabecera NO demuestra autenticidad.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Guarda copias de seguridad de la clave y del archivo original en otro dispositivo.\nPerder la clave o la contraseña puede impedir recuperar los datos.\nHelix-Lock es software beta y no se ha sometido a una auditoría de seguridad independiente."
    },
    "fr": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. Dans l’onglet Fichiers, sélectionnez le fichier source.\n2. Choisissez un mot de passe ou un fichier de clé de 32 octets.\n3. Cliquez sur Chiffrer et choisissez la destination ; conservez l’original.\n4. Pour récupérer les données, sélectionnez le fichier chiffré, utilisez la même clé ou le même mot de passe, puis cliquez sur Déchiffrer.\n5. Vérifiez le fichier récupéré avant de supprimer les sauvegardes.\nF1 ouvre cette aide depuis n’importe quel onglet.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "Fichier source : fichier à traiter.\nFichier de clé : fichier secret contenant 32 octets.\nMot de passe : alternative au fichier de clé.\nChiffrer : crée un fichier chiffré.\nDéchiffrer : restaure le contenu après authentification réussie.\nGénérer une clé : crée une nouvelle clé aléatoire.\nÉcraser : remplace un fichier de sortie existant.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP : format de chiffrement de base.\nHLXN : conteneur chiffré avec le nom de fichier d’origine.\nHLXC / CounterLock : format à compteur de lectures ; vérification distincte du registre requise.\nHLOB : compression expérimentale OBX1 avec AES-GCM.\nHLOM : format Omega expérimental avec réparation GF(256) limitée.\nOBX1 : compression uniquement — PAS de chiffrement.\nHLOB et HLOM ne sont pas des modes standard du bouton Déchiffrer.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP : registre expérimental des identités de clés et des événements.\nChaîne : cohérence locale des entrées.\nSéquence : nombre d’événements.\nPoint de contrôle : vérification indépendante requise.\nAncre de confiance : référence de confiance externe.\nQuorum : majorité requise de témoins indépendants.\nEmpreinte : identifiant d’une clé ou d’un fichier chiffré, PAS la clé secrète.\nFormat : détecter l’en-tête ne prouve PAS l’authenticité.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Conservez des sauvegardes de la clé et du fichier original sur un autre appareil.\nLa perte de la clé ou du mot de passe peut rendre la récupération impossible.\nHelix-Lock est un logiciel bêta qui n’a pas fait l’objet d’un audit de sécurité indépendant."
    }
})

# Complete F1 help for East Asian locales; native-speaker review pending.
merge_catalogs({
    "ja": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. 「ファイル」タブで元のファイルを選択します。\n2. パスワードまたは32バイトの鍵ファイルを選びます。\n3. 「暗号化」をクリックして保存先を指定し、元のファイルを保管してください。\n4. 復元するには暗号化ファイルを選び、同じ鍵またはパスワードを指定して「復号」をクリックします。\n5. バックアップを削除する前に復元したファイルを確認してください。\nF1キーでどのタブからでもこのヘルプを開けます。",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "元のファイル：処理対象のファイル。\n鍵ファイル：32バイトの秘密ファイル。\nパスワード：鍵ファイルの代わりに使用できます。\n暗号化：暗号化ファイルを作成します。\n復号：認証に成功した場合に内容を復元します。\n鍵の生成：新しいランダムな鍵を作成します。\n上書き：既存の出力ファイルを置き換えます。",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP：基本的な暗号化形式。\nHLXN：元のファイル名を含む暗号化コンテナー。\nHLXC / CounterLock：読み取り回数を記録する形式。台帳の別途検証が必要です。\nHLOB：実験的なOBX1圧縮とAES-GCM。\nHLOM：限定的なGF(256)修復を備えた実験的なOmega形式。\nOBX1：圧縮のみで、暗号化はしません。\nHLOBとHLOMは「復号」ボタンの標準モードではありません。",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP：鍵の識別情報とイベントを記録する実験的な台帳。\nChain：記録のローカルな整合性。\nSequence：イベント数。\nCheckpoint：独立した検証が必要です。\nTrust Anchor：外部の信頼基準。\nQuorum：独立した証人の必要多数。\nFingerprint：鍵や暗号文の識別子であり、秘密鍵そのものではありません。\nファイル形式：ヘッダーの検出は真正性の証明ではありません。",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "鍵と元のファイルのバックアップを別の端末に保管してください。\n鍵やパスワードを失うと、データを復元できなくなる可能性があります。\nHelix-Lockはベータ版であり、独立したセキュリティ監査を受けていません。"
    },
    "zh-CN": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. 在“文件”选项卡中选择源文件。\n2. 选择密码或32字节的密钥文件。\n3. 点击“加密”并选择保存位置；请保留原文件。\n4. 如需恢复数据，请选择加密文件，使用相同的密钥或密码，然后点击“解密”。\n5. 删除备份前，请检查恢复后的文件。\n在任意选项卡按F1均可打开本帮助。",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "源文件：要处理的文件。\n密钥文件：包含32字节秘密数据的文件。\n密码：密钥文件的替代方式。\n加密：创建加密文件。\n解密：身份验证成功后恢复内容。\n生成密钥：创建新的随机密钥。\n覆盖：替换已有的输出文件。",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP：基本加密格式。\nHLXN：包含原始文件名的加密容器。\nHLXC / CounterLock：带读取计数器的格式；需要单独验证记录。\nHLOB：实验性的OBX1压缩与AES-GCM。\nHLOM：具有有限GF(256)修复能力的实验性Omega格式。\nOBX1：仅提供压缩，不提供加密。\nHLOB和HLOM不是“解密”按钮的标准模式。",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP：实验性的密钥身份和事件记录。\nChain：本地记录的一致性。\nSequence：事件数量。\nCheckpoint：需要独立验证。\nTrust Anchor：外部信任依据。\nQuorum：独立见证节点所需的多数。\nFingerprint：密钥或密文的标识符，并非秘密密钥。\n文件格式：识别文件头不等于证明真实性。",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "请在其他设备上备份密钥和原始文件。\n丢失密钥或密码可能导致无法恢复数据。\nHelix-Lock仍处于测试阶段，尚未经过独立安全审计。"
    },
    "ko": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. '파일' 탭에서 원본 파일을 선택합니다.\n2. 비밀번호 또는 32바이트 키 파일을 선택합니다.\n3. '암호화'를 누르고 저장 위치를 지정한 뒤 원본을 보관하세요.\n4. 복구하려면 암호화된 파일을 선택하고 같은 키 또는 비밀번호를 입력한 다음 '복호화'를 누릅니다.\n5. 백업을 삭제하기 전에 복구된 파일을 확인하세요.\n어느 탭에서든 F1을 누르면 도움말이 열립니다.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "원본 파일: 처리할 파일입니다.\n키 파일: 32바이트 비밀 데이터가 담긴 파일입니다.\n비밀번호: 키 파일 대신 사용할 수 있습니다.\n암호화: 암호화된 파일을 만듭니다.\n복호화: 인증에 성공하면 내용을 복원합니다.\n키 생성: 새로운 무작위 키를 만듭니다.\n덮어쓰기: 기존 출력 파일을 교체합니다.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: 기본 암호화 형식입니다.\nHLXN: 원래 파일 이름을 포함하는 암호화 컨테이너입니다.\nHLXC / CounterLock: 읽기 횟수 카운터 형식으로, 별도의 기록 검증이 필요합니다.\nHLOB: 실험적인 OBX1 압축 및 AES-GCM입니다.\nHLOM: 제한적인 GF(256) 복구 기능이 있는 실험적인 Omega 형식입니다.\nOBX1: 압축 전용이며 암호화하지 않습니다.\nHLOB 및 HLOM은 '복호화' 버튼의 표준 모드가 아닙니다.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: 키 식별 정보와 이벤트를 기록하는 실험적인 원장입니다.\nChain: 로컬 기록의 일관성입니다.\nSequence: 이벤트 수입니다.\nCheckpoint: 독립적인 검증이 필요합니다.\nTrust Anchor: 외부 신뢰 기준입니다.\nQuorum: 독립적인 증인 중 필요한 과반수입니다.\nFingerprint: 키 또는 암호문의 식별자이며 비밀 키 자체가 아닙니다.\n파일 형식: 헤더 감지는 진위 증명이 아닙니다.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "키와 원본 파일의 백업을 다른 장치에 보관하세요.\n키나 비밀번호를 분실하면 데이터를 복구하지 못할 수 있습니다.\nHelix-Lock은 베타 소프트웨어이며 독립적인 보안 감사를 받지 않았습니다."
    }
})

# F1 help in Italian, European Portuguese and Ukrainian; review pending.
merge_catalogs({
    "it": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. Nella scheda File, seleziona il file sorgente.\n2. Scegli una password o un file chiave di 32 byte.\n3. Fai clic su Cifra e scegli dove salvare; conserva l'originale.\n4. Per recuperare i dati, seleziona il file cifrato, usa la stessa chiave o password e fai clic su Decifra.\n5. Controlla il file recuperato prima di eliminare i backup.\nF1 apre questa guida da qualsiasi scheda.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "File sorgente: file da elaborare.\nFile chiave: file segreto contenente 32 byte.\nPassword: alternativa al file chiave.\nCifra: crea un file cifrato.\nDecifra: ripristina i contenuti dopo l'autenticazione.\nGenera chiave: crea una nuova chiave casuale.\nSovrascrivi: sostituisce un file di output esistente.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: formato di cifratura di base.\nHLXN: contenitore cifrato con il nome originale del file.\nHLXC / CounterLock: formato con contatore di letture; richiede una verifica separata del registro.\nHLOB: compressione sperimentale OBX1 con AES-GCM.\nHLOM: formato Omega sperimentale con riparazione GF(256) limitata.\nOBX1: solo compressione, NON cifra.\nHLOB e HLOM non sono modalità standard del pulsante Decifra.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: registro sperimentale di identità delle chiavi ed eventi.\nChain: coerenza locale delle registrazioni.\nSequence: numero di eventi.\nCheckpoint: richiede una verifica indipendente.\nTrust Anchor: riferimento esterno di fiducia.\nQuorum: maggioranza richiesta di testimoni indipendenti.\nFingerprint: identificatore di chiave o testo cifrato, NON la chiave segreta.\nFormato file: riconoscere l'intestazione NON prova l'autenticità.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Conserva copie di backup della chiave e del file originale su un altro dispositivo.\nLa perdita della chiave o della password può rendere impossibile il recupero.\nHelix-Lock è un software beta e non è stato sottoposto a una verifica di sicurezza indipendente."
    },
    "pt": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. No separador Ficheiros, selecione o ficheiro de origem.\n2. Escolha uma palavra-passe ou um ficheiro de chave de 32 bytes.\n3. Clique em Encriptar e escolha onde guardar; conserve o original.\n4. Para recuperar os dados, selecione o ficheiro encriptado, use a mesma chave ou palavra-passe e clique em Desencriptar.\n5. Verifique o ficheiro recuperado antes de eliminar cópias de segurança.\nF1 abre esta ajuda em qualquer separador.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "Ficheiro de origem: ficheiro a processar.\nFicheiro de chave: ficheiro secreto com 32 bytes.\nPalavra-passe: alternativa ao ficheiro de chave.\nEncriptar: cria um ficheiro encriptado.\nDesencriptar: recupera o conteúdo após autenticação bem-sucedida.\nGerar chave: cria uma nova chave aleatória.\nSubstituir: substitui um ficheiro de saída existente.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: formato básico de encriptação.\nHLXN: contentor encriptado com o nome original do ficheiro.\nHLXC / CounterLock: formato com contador de leituras; requer verificação separada do registo.\nHLOB: compressão experimental OBX1 com AES-GCM.\nHLOM: formato Omega experimental com reparação GF(256) limitada.\nOBX1: apenas compressão — NÃO encripta.\nHLOB e HLOM não são modos padrão do botão Desencriptar.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: registo experimental de identidades de chaves e eventos.\nChain: consistência local das entradas.\nSequence: número de eventos.\nCheckpoint: requer verificação independente.\nTrust Anchor: referência externa de confiança.\nQuorum: maioria necessária de testemunhas independentes.\nFingerprint: identificador de chave ou texto cifrado, NÃO a chave secreta.\nFormato: detetar o cabeçalho NÃO comprova autenticidade.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Guarde cópias de segurança da chave e do ficheiro original noutro dispositivo.\nA perda da chave ou palavra-passe pode impossibilitar a recuperação.\nO Helix-Lock é software beta e não foi sujeito a uma auditoria de segurança independente."
    },
    "uk": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. На вкладці «Файли» виберіть вихідний файл.\n2. Виберіть пароль або файл ключа розміром 32 байти.\n3. Натисніть «Зашифрувати» й виберіть місце збереження; збережіть оригінал.\n4. Для відновлення виберіть зашифрований файл, використайте той самий ключ або пароль і натисніть «Розшифрувати».\n5. Перевірте відновлений файл перед видаленням резервних копій.\nF1 відкриває цю довідку з будь-якої вкладки.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "Вихідний файл: файл для обробки.\nФайл ключа: секретний файл із 32 байтів.\nПароль: альтернатива файлу ключа.\nЗашифрувати: створює зашифрований файл.\nРозшифрувати: відновлює вміст після успішної автентифікації.\nСтворити ключ: створює новий випадковий ключ.\nПерезаписати: замінює наявний вихідний файл.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: базовий формат шифрування.\nHLXN: зашифрований контейнер із початковою назвою файлу.\nHLXC / CounterLock: формат із лічильником читань; потребує окремої перевірки журналу.\nHLOB: експериментальне стиснення OBX1 з AES-GCM.\nHLOM: експериментальний формат Omega з обмеженим відновленням GF(256).\nOBX1: лише стиснення — НЕ шифрує.\nHLOB і HLOM не є стандартними режимами кнопки «Розшифрувати».",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: експериментальний журнал ідентичностей ключів і подій.\nChain: локальна узгодженість записів.\nSequence: кількість подій.\nCheckpoint: потребує незалежної перевірки.\nTrust Anchor: зовнішній орієнтир довіри.\nQuorum: необхідна більшість незалежних свідків.\nFingerprint: ідентифікатор ключа або шифротексту, НЕ секретний ключ.\nФормат файлу: розпізнавання заголовка НЕ доводить справжність.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Зберігайте резервні копії ключа й вихідного файлу на іншому пристрої.\nВтрата ключа або пароля може унеможливити відновлення.\nHelix-Lock — бета-версія, яка не проходила незалежний аудит безпеки."
    }
})

# F1 help in Hindi, Indonesian, Vietnamese and Thai; native review pending.
merge_catalogs({
    "hi": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. फ़ाइलें टैब में स्रोत फ़ाइल चुनें।\n2. पासवर्ड या 32-बाइट की कुंजी फ़ाइल चुनें।\n3. एन्क्रिप्ट पर क्लिक करें और सहेजने की जगह चुनें; मूल फ़ाइल सुरक्षित रखें।\n4. डेटा वापस पाने के लिए एन्क्रिप्ट की गई फ़ाइल चुनें, वही कुंजी या पासवर्ड दें और डिक्रिप्ट पर क्लिक करें।\n5. बैकअप हटाने से पहले पुनर्प्राप्त फ़ाइल जाँचें।\nकिसी भी टैब से F1 दबाकर यह सहायता खोलें।",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "स्रोत फ़ाइल: संसाधित की जाने वाली फ़ाइल।\nकुंजी फ़ाइल: 32 बाइट वाली गोपनीय फ़ाइल।\nपासवर्ड: कुंजी फ़ाइल का विकल्प।\nएन्क्रिप्ट: एन्क्रिप्ट की गई फ़ाइल बनाता है।\nडिक्रिप्ट: सफल प्रमाणीकरण के बाद सामग्री लौटाता है।\nकुंजी बनाएँ: नई यादृच्छिक कुंजी बनाता है।\nओवरराइट: मौजूदा आउटपुट फ़ाइल को बदलता है।",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: मूल एन्क्रिप्शन प्रारूप।\nHLXN: मूल फ़ाइल नाम वाला एन्क्रिप्टेड कंटेनर।\nHLXC / CounterLock: पढ़ने की संख्या वाला प्रारूप; रिकॉर्ड का अलग सत्यापन आवश्यक है।\nHLOB: प्रयोगात्मक OBX1 संपीड़न और AES-GCM।\nHLOM: सीमित GF(256) मरम्मत वाला प्रयोगात्मक Omega प्रारूप।\nOBX1: केवल संपीड़न — एन्क्रिप्शन नहीं।\nHLOB और HLOM डिक्रिप्ट बटन के मानक मोड नहीं हैं।",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: कुंजी पहचान और घटनाओं का प्रयोगात्मक रिकॉर्ड।\nChain: स्थानीय प्रविष्टियों की संगति।\nSequence: घटनाओं की संख्या।\nCheckpoint: स्वतंत्र सत्यापन आवश्यक है।\nTrust Anchor: बाहरी विश्वास संदर्भ।\nQuorum: स्वतंत्र गवाहों का आवश्यक बहुमत।\nFingerprint: कुंजी या एन्क्रिप्टेड डेटा का पहचानकर्ता, गोपनीय कुंजी नहीं।\nफ़ाइल प्रारूप: हेडर पहचानना प्रामाणिकता का प्रमाण नहीं है।",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "कुंजी और मूल फ़ाइल का बैकअप किसी दूसरे उपकरण पर रखें।\nकुंजी या पासवर्ड खोने पर डेटा वापस पाना असंभव हो सकता है।\nHelix-Lock बीटा सॉफ़्टवेयर है और इसका स्वतंत्र सुरक्षा ऑडिट नहीं हुआ है।"
    },
    "id": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. Pada tab Berkas, pilih berkas sumber.\n2. Pilih kata sandi atau berkas kunci berukuran 32 byte.\n3. Klik Enkripsi dan pilih lokasi penyimpanan; simpan berkas asli.\n4. Untuk memulihkan data, pilih berkas terenkripsi, gunakan kunci atau kata sandi yang sama, lalu klik Dekripsi.\n5. Periksa berkas hasil pemulihan sebelum menghapus cadangan.\nTekan F1 untuk membuka bantuan ini dari tab mana pun.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "Berkas sumber: berkas yang akan diproses.\nBerkas kunci: berkas rahasia berisi 32 byte.\nKata sandi: alternatif berkas kunci.\nEnkripsi: membuat berkas terenkripsi.\nDekripsi: memulihkan isi setelah autentikasi berhasil.\nBuat kunci: membuat kunci acak baru.\nTimpa: mengganti berkas keluaran yang sudah ada.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: format enkripsi dasar.\nHLXN: wadah terenkripsi dengan nama berkas asli.\nHLXC / CounterLock: format penghitung pembacaan; catatan harus diverifikasi secara terpisah.\nHLOB: kompresi OBX1 eksperimental dengan AES-GCM.\nHLOM: format Omega eksperimental dengan perbaikan GF(256) terbatas.\nOBX1: hanya kompresi — BUKAN enkripsi.\nHLOB dan HLOM bukan mode standar tombol Dekripsi.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: catatan eksperimental identitas kunci dan peristiwa.\nChain: konsistensi entri lokal.\nSequence: jumlah peristiwa.\nCheckpoint: memerlukan verifikasi independen.\nTrust Anchor: acuan kepercayaan eksternal.\nQuorum: mayoritas saksi independen yang diperlukan.\nFingerprint: pengenal kunci atau data terenkripsi, BUKAN kunci rahasia.\nFormat berkas: deteksi header BUKAN bukti keaslian.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Simpan cadangan kunci dan berkas asli di perangkat lain.\nKehilangan kunci atau kata sandi dapat membuat pemulihan mustahil.\nHelix-Lock adalah perangkat lunak beta dan belum menjalani audit keamanan independen."
    },
    "vi": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. Trong thẻ Tệp, chọn tệp nguồn.\n2. Chọn mật khẩu hoặc tệp khóa 32 byte.\n3. Nhấn Mã hóa và chọn nơi lưu; giữ lại tệp gốc.\n4. Để khôi phục dữ liệu, chọn tệp đã mã hóa, dùng cùng khóa hoặc mật khẩu rồi nhấn Giải mã.\n5. Kiểm tra tệp đã khôi phục trước khi xóa bản sao lưu.\nNhấn F1 để mở trợ giúp từ bất kỳ thẻ nào.",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "Tệp nguồn: tệp cần xử lý.\nTệp khóa: tệp bí mật chứa 32 byte.\nMật khẩu: phương án thay thế tệp khóa.\nMã hóa: tạo tệp được mã hóa.\nGiải mã: khôi phục nội dung sau khi xác thực thành công.\nTạo khóa: tạo khóa ngẫu nhiên mới.\nGhi đè: thay thế tệp đầu ra hiện có.",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: định dạng mã hóa cơ bản.\nHLXN: vùng chứa mã hóa giữ tên tệp gốc.\nHLXC / CounterLock: định dạng có bộ đếm lượt đọc; cần kiểm tra nhật ký riêng.\nHLOB: nén OBX1 thử nghiệm kết hợp AES-GCM.\nHLOM: định dạng Omega thử nghiệm với khả năng sửa GF(256) hạn chế.\nOBX1: chỉ nén — KHÔNG mã hóa.\nHLOB và HLOM không phải chế độ tiêu chuẩn của nút Giải mã.",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: nhật ký thử nghiệm về danh tính khóa và sự kiện.\nChain: tính nhất quán của các mục ghi cục bộ.\nSequence: số sự kiện.\nCheckpoint: cần xác minh độc lập.\nTrust Anchor: tham chiếu tin cậy bên ngoài.\nQuorum: đa số cần thiết của các nhân chứng độc lập.\nFingerprint: mã định danh khóa hoặc bản mã, KHÔNG phải khóa bí mật.\nĐịnh dạng tệp: nhận diện phần đầu KHÔNG chứng minh tính xác thực.",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "Lưu bản sao khóa và tệp gốc trên thiết bị khác.\nMất khóa hoặc mật khẩu có thể khiến việc khôi phục không thể thực hiện.\nHelix-Lock là phần mềm beta và chưa trải qua kiểm toán bảo mật độc lập."
    },
    "th": {
        "1. On the Files tab, select the source file.\n2. Choose a password or a 32-byte key file.\n3. Click Encrypt and choose an output path; keep the original.\n4. To recover data, select the encrypted file, use the same key or password, and click Decrypt.\n5. Check the recovered file before deleting backups.\nF1 opens this help from any tab.": "1. ในแท็บไฟล์ ให้เลือกไฟล์ต้นฉบับ\n2. เลือกรหัสผ่านหรือไฟล์กุญแจขนาด 32 ไบต์\n3. คลิกเข้ารหัสและเลือกตำแหน่งบันทึก โดยเก็บไฟล์ต้นฉบับไว้\n4. หากต้องการกู้คืน ให้เลือกไฟล์ที่เข้ารหัส ใช้กุญแจหรือรหัสผ่านเดิม แล้วคลิกถอดรหัส\n5. ตรวจสอบไฟล์ที่กู้คืนก่อนลบข้อมูลสำรอง\nกด F1 เพื่อเปิดวิธีใช้นี้จากแท็บใดก็ได้",
        "Source file: the file to process.\nKey file: a secret file containing 32 bytes.\nPassword: an alternative to a key file.\nEncrypt: creates an encrypted file.\nDecrypt: restores content after successful authentication.\nGenerate key: creates a new random key.\nOverwrite: replaces an existing output file.": "ไฟล์ต้นฉบับ: ไฟล์ที่ต้องการประมวลผล\nไฟล์กุญแจ: ไฟล์ลับที่มีข้อมูล 32 ไบต์\nรหัสผ่าน: ทางเลือกแทนไฟล์กุญแจ\nเข้ารหัส: สร้างไฟล์ที่เข้ารหัส\nถอดรหัส: กู้คืนเนื้อหาหลังยืนยันตัวตนสำเร็จ\nสร้างกุญแจ: สร้างกุญแจแบบสุ่มใหม่\nเขียนทับ: แทนที่ไฟล์ผลลัพธ์ที่มีอยู่",
        "HLXP: basic encryption format.\nHLXN: encrypted container with the original filename.\nHLXC / CounterLock: read-counter format; requires separate ledger verification.\nHLOB: experimental OBX1 compression plus AES-GCM.\nHLOM: experimental Omega format with limited GF(256) repair.\nOBX1: compression codec only — NOT encryption.\nHLOB and HLOM are not standard modes of the Decrypt button.": "HLXP: รูปแบบการเข้ารหัสพื้นฐาน\nHLXN: คอนเทนเนอร์เข้ารหัสที่เก็บชื่อไฟล์เดิม\nHLXC / CounterLock: รูปแบบที่มีตัวนับการอ่าน ต้องตรวจสอบบันทึกแยกต่างหาก\nHLOB: การบีบอัด OBX1 แบบทดลองร่วมกับ AES-GCM\nHLOM: รูปแบบ Omega แบบทดลองที่ซ่อมแซม GF(256) ได้อย่างจำกัด\nOBX1: บีบอัดเท่านั้น — ไม่ใช่การเข้ารหัส\nHLOB และ HLOM ไม่ใช่โหมดมาตรฐานของปุ่มถอดรหัส",
        "AIRP: experimental key identity and event ledger.\nChain: local consistency of ledger entries.\nSequence: number of events.\nCheckpoint: requires independent verification.\nTrust Anchor: external trust reference.\nQuorum: required majority of independent witnesses.\nFingerprint: identifier of a key or ciphertext, NOT the secret key.\nFile format: header detection, NOT proof of authenticity.": "AIRP: บันทึกข้อมูลระบุกุญแจและเหตุการณ์แบบทดลอง\nChain: ความสอดคล้องของรายการในเครื่อง\nSequence: จำนวนเหตุการณ์\nCheckpoint: ต้องมีการตรวจสอบอย่างอิสระ\nTrust Anchor: แหล่งอ้างอิงความเชื่อถือภายนอก\nQuorum: เสียงข้างมากที่ต้องการจากพยานอิสระ\nFingerprint: ตัวระบุกุญแจหรือข้อมูลเข้ารหัส ไม่ใช่กุญแจลับ\nรูปแบบไฟล์: การตรวจพบส่วนหัวไม่ใช่หลักฐานยืนยันความถูกต้องแท้จริง",
        "Keep backups of the key and original file on a separate device.\nLosing the key or password may make recovery impossible.\nHelix-Lock is beta software and has not undergone an independent security audit.": "เก็บสำเนาสำรองของกุญแจและไฟล์ต้นฉบับไว้ในอุปกรณ์อื่น\nหากกุญแจหรือรหัสผ่านสูญหาย อาจไม่สามารถกู้คืนข้อมูลได้\nHelix-Lock เป็นซอฟต์แวร์เบตาและยังไม่ได้ผ่านการตรวจสอบความปลอดภัยโดยหน่วยงานอิสระ"
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
