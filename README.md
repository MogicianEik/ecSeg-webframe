# ecSeg-webframe
The server-ready webframe work of ecSeg written by Yichi Zhang (MogicianEik, yiz370@ucsd.edu).

ecSeg-webframe is a python3-Django based webframe and is an extension of [ecSeg](https://github.com/UCRajkumar/ecSeg), Semantic Segmentation of Metaphase Images containing Extrachromosomal DNA
Utkrisht Rajkumar, Kristen Turner, Jens Luebeck, Viraj Deshpande, Manmohan Chandraker, Paul Mischel, and Dr. Vineet Bafna.

There are two major brances:
1. master branch contains the server-ready ecSeg-webframe
2. clean-backup contains an empty image-processing webframe which is ready for any plug-in core functions. Developers only needs to revise 'ai_functions.py' and let it read outputs from the core function and the webframe will take care the rest.

For anyone who firstly use the webframe: Pyhton 3 is required. (3.5 for running certain tensorflow models)
```
git clone https://github.com/MogicianEik/ecSeg-webframe
cd ecSeg-webframe
pip3 install -r requirements.txt (ecSeg is incoporated and there is no need to download/install ecSeg again)
python3 manage.py makemigrations analyze
python3 manage.py migrate analyze
python3 manage.py migrate
```

Important notice:
For using ecSeg-webframe normally, please revise 2 lines inside the "time_consuming_task" function of the script "ai_function.py" according to notes in the script to make sure a direct python path is provided.

Here is a quick demo of how this webframe works:
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/FnQXlUfcdYg/0.jpg)](http://www.youtube.com/watch?v=FnQXlUfcdYg)

