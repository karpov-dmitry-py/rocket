FROM ubuntu:20.04

RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python3.8 -y
RUN apt install python3-pip -y
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3.8 /usr/bin/python

RUN apt install curl -y
RUN apt install unzip -y
RUN apt install wget -y
RUN apt install xvfb -y
RUN apt install libpcre3 -y
RUN apt install libpcre3-dev -y
RUN apt install packagekit-gtk3-module -y
RUN apt install libgtk-3-0 -y
RUN apt install libdbus-glib-1-2
RUN apt install dpkg -y

RUN apt install -y locales locales-all
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING utf-8

# install phantomjs
# RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
#     tar -jxf phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
#     cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs && \
#     rm phantomjs-2.1.1-linux-x86_64.tar.bz2



# install geckodriver and firefox
RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN apt purge firefox
RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

# install chromedriver and google-chrome
# RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
#     wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
#     unzip chromedriver_linux64.zip -d /usr/bin && \
#     chmod +x /usr/bin/chromedriver && \
#     rm chromedriver_linux64.zip
#
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list
# RUN apt update
# RUN apt install google-chrome-stable -y
#
# RUN CHROME_SETUP=google-chrome.deb && \
#     wget -O $CHROME_SETUP "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" && \
#     dpkg -i $CHROME_SETUP && \
#     apt-get install -y -f && \
#     rm $CHROME_SETUP

# set uids and gids env variables
ENV usr dockeruser
ENV grp dockeruser

# prepare home directory
RUN mkdir -p /home/$usr/
RUN groupadd -g 1000 $grp && \
    useradd -r -u 1000 -g $grp -d /home/$usr/ $usr
RUN chown -R $usr:$grp /home/$usr/
# from now we work not under root

# EXPOSE 8080

# copy app dir, install dependencies and run entry_point bash script
USER $usr
RUN mkdir -p /home/$usr/workdir
COPY ecom /home/$usr/workdir

RUN mkdir -p /home/$usr/parsing_results/category

USER root
RUN chmod -R 777 /home/$usr/workdir
RUN chmod -R 777 /home/$usr/parsing_results/category

USER $usr
RUN pip3 install --user -r /home/$usr/workdir/requirements.txt
ENTRYPOINT /home/dockeruser/.local/bin/uwsgi /home/$usr/workdir/uwsgi.ini
