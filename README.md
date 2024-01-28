# AuxVocabTest  
 auxiliary tools for my vocabulary tests (windows / linux)  

***

## Try  
1. Install selenium.  
    ```shell
    pip install selenium
    ```
2. Copy ```config_sample.ini``` to ```config.ini``` and change the parameters in ```config.ini```if you want.  
3. Add these contents to ```private.txt``` (UTF-8 encoding). Make sure it's in the same directory as the .py files.
   ```
   https://www.google.com/
   1
   小明
   %USERPROFILE%/
   $HOME/
   1
   ```
4. Run ```python [filename].py``` in the shell to enjoy.  
5. If you don't have firefox or geckodriver (firefox webdriver) installed, The first time you start the program, it will download by itself. This may cost you a minute or two.  
**Just wait patiently, or install them by yourself.**  

***

## Note  
1. data.txt (used in aux_vocab_test_SAT) will not be provided, but here is an example line of that file:  
   ```
   1|apex|n.|顶点；最高点|the top or highest part of sth
   ```
2. Because the SAT vocabulary test website cannot be published, ```private.txt``` uses google.com for instead.  
3. cookie.json (used in aux_vocab_test_SAT) will not be provided.