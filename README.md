ScandalOh_backend
=================

Parte del servidor.

Necesario instalar ffmpeg en sistema

En terminal escribe sudo apt-get install ffmpeg
Después escribe sudo apt-get install ffmpeg libavcodec-extra-53

Ejecutar también lo siguiente para activar el encoder de jpeg.
pip uninstall PIL
apt-get install libjpeg-dev
apt-get install zlib1g-dev
apt-get install libpng12-dev
$ sudo apt-get install python-dev libjpeg-dev libfreetype6-dev zlib1g-dev
$ sudo ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
$ sudo ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
$ sudo ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/
pip install PIL