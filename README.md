# puyopuyo_rl
This contains puyopuyo environment for gym.

# Preparation
First, you need to download  puyopuyo image from [here](https://puyo-camp.jp/posts/157768)
Then, put that in ./img folder. After that, run `python ./img/split_img.py` to split the images.

# Requirements
This environment uses pygame to render puyopuyo board.
And, OpenCV for `./img/split_img.py`.
```
pip install pygame opencv-python
```

