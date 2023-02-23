Search.setIndex({"docnames": ["contributing", "how_to_write_custom_backend", "index", "usage"], "filenames": ["contributing.rst", "how_to_write_custom_backend.rst", "index.rst", "usage.rst"], "titles": ["Project Setup", "How to write custom backend?", "&lt;no title&gt;", "How to Use Django Phone Verify?"], "terms": {"thank": 0, "you": [0, 1, 3], "your": [0, 1, 3], "interest": 0, "contribut": 0, "thi": [0, 1, 3], "The": [0, 1], "follow": [0, 3], "set": [0, 1, 3], "step": [0, 1], "should": [0, 1, 3], "help": 0, "get": [0, 1, 3], "start": 0, "django": [0, 2], "phone": [0, 1, 2], "verifi": [0, 1, 2], "clone": 0, "git": 0, "repositori": 0, "onto": 0, "system": 0, "http": 0, "github": 0, "com": [0, 3], "curiouslearn": 0, "creat": [0, 2, 3], "virtual": 0, "environ": [0, 1], "mai": [0, 1], "us": [0, 1, 2], "ani": [0, 1], "tool": 0, "choic": 0, "python3": 0, "m": 0, "venv": 0, "activ": 0, "env": 0, "sourc": 0, "bin": 0, "instal": [0, 2], "python": [0, 3], "depend": 0, "via": [0, 3], "command": 0, "make": 0, "sure": [0, 1], "ar": [0, 3], "root": 0, "directori": 0, "pip": [0, 3], "r": 0, "requir": [0, 1, 3], "txt": 0, "That": 0, "": [0, 1, 3], "now": 0, "have": [0, 1], "can": [0, 1, 3], "ha": [0, 1], "unit": 0, "locat": 0, "pytest": 0, "write": [0, 2], "befor": [0, 2], "we": [0, 1, 3], "proce": [0, 1, 3], "perform": [0, 3], "To": [0, 3], "If": [0, 1, 3], "want": [0, 1, 3], "code": [0, 1, 3], "coverag": 0, "cov": 0, "argument": [0, 1], "list": [0, 3], "down": 0, "current": 0, "chang": 0, "differ": 0, "version": 0, "support": 0, "tox": 0, "like": [0, 3], "would": [0, 3], "all": [0, 1, 3], "combin": 0, "check": [0, 3], "ini": 0, "file": [0, 1, 3], "more": [0, 1], "detail": [0, 3], "onc": 0, "ve": 0, "made": 0, "copi": 0, "app": [0, 1, 3], "e": 0, "flag": 0, "manner": 0, "cd": 0, "path": [0, 1], "new": [0, 1, 3], "modifi": 0, "applic": 0, "rather": 0, "than": [0, 1], "fetch": [0, 1], "from": [0, 1, 3], "pypi": 0, "after": [0, 2], "re": 0, "satisfi": 0, "section": 0, "abov": [0, 1, 3], "In": [1, 3], "case": [1, 2], "anyth": 1, "other": 1, "provid": [1, 3], "phone_verifi": [1, 3], "nexmo": 1, "nexmobackend": 1, "twilio": [1, 3], "twiliobackend": [1, 3], "extend": [1, 3], "base": [1, 3], "basebackend": 1, "shown": [1, 3], "below": [1, 3], "note": [1, 3], "For": [1, 3], "tutori": 1, "consid": 1, "remain": 1, "same": 1, "name": 1, "within": 1, "project": [1, 2], "let": 1, "sai": 1, "py": [1, 3], "defin": 1, "phone_verif": [1, 3], "class": [1, 3], "which": [1, 3], "further": [1, 3], "option": [1, 3], "kei": 1, "fake": [1, 3], "secret": [1, 3], "1232328372987": 1, "sandbox_token": [1, 3], "123456": [1, 3], "util": 1, "token_length": [1, 3], "6": [1, 3], "messag": [1, 3], "welcom": [1, 3], "pleas": [1, 3], "secur": [1, 3], "security_cod": [1, 3], "app_nam": [1, 3], "security_code_expiration_tim": [1, 3], "3600": [1, 3], "second": [1, 3], "onli": [1, 3], "verify_security_code_only_onc": [1, 3], "true": [1, 3], "fals": [1, 3], "multipl": [1, 3], "time": [1, 2], "verif": [1, 3], "client": 1, "avail": [1, 3], "send": 1, "sm": 1, "directli": 1, "api": [1, 3], "sinc": 1, "call": 1, "leverag": [1, 3], "its": [1, 3], "function": [1, 3], "must": [1, 3], "inherit": [1, 3], "third": 1, "parti": 1, "stuff": 1, "import": [1, 3], "def": [1, 3], "__init__": 1, "self": [1, 3], "super": 1, "lower": 1, "just": [1, 3], "valu": 1, "item": 1, "_kei": 1, "none": [1, 3], "_secret": 1, "_from": 1, "object": [1, 3], "initi": 1, "constructor": 1, "dictionari": 1, "contain": 1, "specif": 1, "each": 1, "piec": 1, "apart": 1, "our": 1, "necessari": 1, "overrid": [1, 3], "send_sm": 1, "method": [1, 3], "implement": 1, "It": [1, 3], "two": 1, "posit": 1, "paramet": 1, "number": [1, 2], "respect": 1, "send_messag": 1, "text": 1, "bulk": 1, "send_bulk_sm": 1, "wish": 1, "ll": [1, 3], "keep": 1, "mind": 1, "need": [1, 3], "few": [1, 3], "tweak": 1, "bit": 1, "nexmosandboxbackend": 1, "enabl": 1, "token": 1, "constant": 1, "test": [1, 2], "purpos": 1, "done": 1, "actual": 1, "model": [1, 3], "smsverif": [1, 3], "_token": 1, "generate_security_cod": 1, "return": [1, 3], "fix": 1, "validate_security_cod": 1, "phone_numb": [1, 3], "session_token": [1, 3], "alwai": 1, "valid": 1, "security_code_valid": 1, "also": [1, 3], "overriden": 1, "an": [1, 3], "empti": 1, "uniform": 1, "acut": 1, "order": 1, "replac": 1, "under": 1, "how": 2, "configur": 2, "usag": 2, "1": 2, "user": 2, "registr": 2, "2": 2, "custom": [2, 3], "backend": [2, 3], "sandbox": 2, "servic": [2, 3], "setup": 2, "run": 2, "local": 2, "develop": 2, "add": 3, "installed_app": 3, "sid": 3, "14755292729": 3, "migrat": 3, "databas": 3, "manag": 3, "tabl": 3, "i": 3, "store": 3, "ad": 3, "endpoint": 3, "Its": 3, "explain": 3, "suitabl": 3, "simpli": 3, "access": 3, "regist": 3, "api_endpoint": 3, "rst": 3, "updat": 3, "url": 3, "default": 3, "router": 3, "rest_framework": 3, "defaultrout": 3, "verificationviewset": 3, "default_rout": 3, "trailing_slash": 3, "basenam": 3, "urlpattern": 3, "recommend": 3, "when": 3, "choos": 3, "integr": 3, "process": 3, "here": 3, "first": 3, "verify_and_regist": 3, "success": 3, "redirect": 3, "one": 3, "viewset": 3, "yourapp": 3, "yourcustomviewset": 3, "yourcustomseri": 3, "serial": 3, "smsverificationseri": 3, "youruserseri": 3, "usernam": 3, "charfield": 3, "email": 3, "emailfield": 3, "password": 3, "first_nam": 3, "userseri": 3, "contrib": 3, "auth": 3, "get_user_model": 3, "create_user_account": 3, "extra_arg": 3, "create_us": 3, "decor": 3, "action": 3, "permiss": 3, "allowani": 3, "respons": 3, "phone_seri": 3, "post": 3, "permission_class": 3, "serializer_class": 3, "request": 3, "most": 3, "correspond": 3, "view": 3, "alreadi": 3, "present": 3, "packag": 3, "data": 3, "is_valid": 3, "raise_except": 3, "exampl": 3, "validated_data": 3, "coupl": 3, "One": 3, "addit": 3, "compani": 3, "etc": 3, "get_serializer_class": 3, "specifi": 3, "condit": 3, "els": 3, "otherwis": 3, "latest": 3, "gener": 3, "found": 3, "admin": 3, "post_sav": 3, "signal": 3, "through": 3, "hook": 3, "receiv": 3, "db": 3, "dispatch": 3, "core": 3, "mail": 3, "send_mail": 3, "send_phone_verify_email": 3, "fire": 3, "entri": 3, "instanc": 3, "sender": 3, "kwarg": 3, "subject": 3, "from_email": 3, "recipient_list": 3, "fail_sil": 3}, "objects": {}, "objtypes": {}, "objnames": {}, "titleterms": {"project": 0, "setup": 0, "run": 0, "test": 0, "local": 0, "develop": 0, "how": [1, 3], "write": 1, "custom": 1, "backend": 1, "creat": 1, "sandbox": 1, "servic": 1, "content": 2, "us": 3, "django": 3, "phone": 3, "verifi": 3, "instal": 3, "configur": 3, "usag": 3, "case": 3, "1": 3, "number": 3, "befor": 3, "after": 3, "user": 3, "registr": 3, "2": 3, "time": 3}, "envversion": {"sphinx.domains.c": 2, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 8, "sphinx.domains.index": 1, "sphinx.domains.javascript": 2, "sphinx.domains.math": 2, "sphinx.domains.python": 3, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx": 57}, "alltitles": {"Project Setup": [[0, "project-setup"]], "Running Tests": [[0, "running-tests"]], "Local Development and testing": [[0, "local-development-and-testing"]], "How to write custom backend?": [[1, "how-to-write-custom-backend"]], "How to create custom Sandbox Service?": [[1, "how-to-create-custom-sandbox-service"]], "Contents:": [[2, null]], "How to Use Django Phone Verify?": [[3, "how-to-use-django-phone-verify"]], "Installation": [[3, "installation"]], "Configuration": [[3, "configuration"]], "Usage": [[3, "usage"]], "Case 1: Verify phone number before/after user registration": [[3, "case-1-verify-phone-number-before-after-user-registration"]], "Case 2: Verify phone number at the time of user registration": [[3, "case-2-verify-phone-number-at-the-time-of-user-registration"]]}, "indexentries": {}})