# TranslateRenPy
TranslateRenPy

Author: duc010298-1


## Features

- Unlimited number of characters to be translated
- Using selenium to translate (no need Yandex API key or Google Cloud Services - free for all)
- Automatically override available languages (you do not need renpy sdk to Generate Translations)
- Automatically ignores variables or special characters of Renpy during translation:
    ### Example
    1. `[earnings]` is kept after translation
        ```
        # m "OK, let's check the school's account. The school's owners have transferred me [earnings] credits."
        m "OK, vérifions le compte de l'école. Les propriétaires de l'école m'ont transféré [earnings] crédits."
        ```
    2. `\n` (break line) is kept after translation
        ```
        old "Loading will lose unsaved progress.\nAre you sure you want to do this?"
        new "Le chargement perdra la progression non enregistrée.\nEs-tu sûr de vouloir faire ça?"
        ```
    3. `%s` is kept after translation
        ```
        old "Saved screenshot as %s."
        new "Capture d'écran enregistrée sous %s."
        ```
    And some other special cases

## Quick Start

### Installation instructions

1. Install Python

    You need Python 3 or later to run translate-renpy
    
    For Windows, packages are available at
    
    https://www.python.org/getit/

2. Install requirements

    Clone or download zip source code, open Command line in source code folder
    
    Install requirements using `pip`:
    
        pip install -r requirements.txt

3. Install Driver

    You should instal Chrome browser and check your browser version
    
    And then download ChromeDriver suitable for your browser at: [chromedriver.chromium.org](https://chromedriver.chromium.org/)
    
    After downloaded, extract it, copy and rewrite `chromedriver` to folder `Driver\[your_os]` in source code folder

### Usage

1. First you need generate RenPy translations

    You can read and follow Generate RenPy translations section on this post: 
    
    [F95 RenPy Translation tool](https://f95zone.to/threads/renpy-translation-tool.21920/)

    ** Note: Some games do not compile rpyc files. If in the folder `[your_game]\game\tl\[language]` there are many files with .rpy extension look like on screen below, you can skip this step.
    
    ![preview](https://i.imgur.com/qwSUosi.png)
    
2. Run `run.bat` file

    For original language and into language, you should go to cloud.google.com/translate/docs/languages and find ISO-639-1 Code of your language

    Number of thread, this is the number of browser tabs the tool will open simultaneously (I recommended 16 for 8Gb Ram)

    You can show the browser during translation but I recommend you to hide it to avoid using too much CPU.

### Help me
- Please Star this github repository if it is of help to you
