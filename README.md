<h1 align="center">TitanML | Arxiv Chat</h1>


<p align="center">
  <img src="https://github.com/titanml/arxiv-chat/blob/e23a521086d32e7d69a7628c4923a02d75c0a682/static/799480_An%20enormous%20library%20which%20is%20many%20floors%20tall%2C%20the_xl-1024-v1-0.png" alt="Image from TitanML">
</p>

<p align="center">
  <a href="#green_book-about">About</a> &#xa0; | &#xa0; 
  <a href="#computer-development">Development</a> &#xa0; &#xa0;
</p>

## :green_book: About ##

This the repo for a flan-t5-xl based Arxiv interaction platform, for summarizing and asking questions about Arxiv papers. For details on the theory behind the app, check out our blog [here](gitbooks.com). The frontend is built and served using [Streamlit](https://streamlit.io), and individual models are accessed using simple [FastApi](https://fastapi.tiangolo.com) servers. The vector database required for question answering is designed using a modified version of [VLite](https://github.com/vlitejs/vlite) - specifically the text chunking functionality is customised, and can be easily overwritten in _/embeddings/app/vlite/utils.py_. 

## :computer: Development ##

To run this app yourself requires Docker. 3 apps need to be built individually, and then unified with Docker Compose. \
From in _/src_, run:
``` 
docker build -t frontend .
```
From in _/embeddings_, run:
``` 
docker build -t embeddings .
```
Download the [Titan Takeoff](https://github.com/titanml/takeoff) repo, and build the image:
``` 
docker build -t takeoff .
```

All endpoints can be customised to match the needs of your models. The summarizer and Q&A models need to be downloaded and accessible, to be volume mounted into the Takeoff container - follow instructions at the specific repo for how to setup.

To run the whole system, navigate to _/docker_ and run:
```
docker compose up
```