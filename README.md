# Simple restful web service

The task condition can be viewed [here](TASK.pdf).

---

This application consists of several parts:
- storage: *tarantool*
- python application: *falcon* + *gunicorn*
- web-server: *nginx*

## Design
Plain scheme showing the architecture of the application:

![design](https://i.imgur.com/sNdWDtp.png)

## Installation (Ubuntu)

**First step** - install database - tarantool.

There are many ways, an example of how to take a fresh branch of [source](https://github.com/tarantool/tarantool/tree/2.2)

And build by [instruction](https://www.tarantool.io/en/doc/2.2/dev_guide/building_from_source/) 

---

**Next step** - install app

All operations are performed with *python3.6.8*

First you have to take the project repository:

Say:

```bash
git clone https://github.com/vanyarock01/yappcity.git
cd yappcity
```
---

Install a virtual environment

```bash
sudo apt-get install python-virtualenv
```

Сreate with command

```bash
sudo virtualenv -p python3 ./gift_service/.venv
```

And last - activate

```bash
sudo ./gift_service/ ./gift_service/.venv/bin/activate
```
---

Next we will install the necessary dependencies and components

```bash
pip3 install -r requirements.txt
sudo apt-get install gunicorn
sudo apt-get install nginx
```

Fine, that's all.

## Run

- Set up tarantool instance

```bash
cd storage/
tarantool storage.lua
```

To check, you can execute the command `ps aux | grep tarantool`

Example of a successful search:
```bash
user     20955  0.2  0.7 764864 63160 ?        Ssl  00:35   0:00 tarantool storage.lua <running>
```

---

Next we go to start the web application

```bash
cd ../gift_service
gunicorn -w 9 -b 0.0.0.0:5000 --reload app:api
```

I advise you to count the number of workers according to the

`(2 x $num_cores == 4) + 1`

An example of a command to know the number of cores:

`grep -c ^processor /proc/cpuinfo`

---

Finally, it remains to run **nginx**

Say:
```bash
cd deployment
sudo cp gift_service.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/gift_service.conf /etc/nginx/sites-enabled/gift_service.conf
sudo nginx -t

sudo systemctl restart nginx 
```

It's done.

## Test

The tests are written on the **pytest**

To start up, say:

```bash
cd tests/
python3.6 -m pytest -v

```

If successful, you'll get it:

```
================================ test session starts ================================
platform linux -- Python 3.6.8, pytest-5.1.0, py-1.8.0, pluggy-0.12.0 -- /usr/bin/python3.6
cachedir: .pytest_cache
collected 20 items                                                                  

test_bad_request.py::test_empty_data_on_post PASSED                           [  5%]
test_bad_request.py::test_empty_citizen_list_on_post PASSED                   [ 10%]
test_bad_request.py::test_bad_data_on_post PASSED                             [ 15%]
test_bad_request.py::test_bad_json_on_post PASSED                             [ 20%]
test_bad_request.py::test_check_type_params_patch_type PASSED                 [ 25%]
test_bad_request.py::test_check_type_params_patch_value PASSED                [ 30%]
test_bad_request.py::test_bad_patch_body_empty PASSED                         [ 35%]
test_bad_request.py::test_bad_patch_body_type_list PASSED                     [ 40%]
test_bad_request.py::test_bad_patch_body_type_string PASSED                   [ 45%]
test_birtdays.py::test_birthdays PASSED                                       [ 50%]
test_parallel_request.py::test_post_get PASSED                                [ 55%]
test_parallel_request.py::test_patch PASSED                                   [ 60%]
test_patch.py::test_invalid PASSED                                            [ 65%]
test_patch.py::test_patch PASSED                                              [ 70%]
test_patch.py::test_patch_all_relatives_timeout PASSED                        [ 75%]
test_percentile.py::test_percentile PASSED                                    [ 80%]
test_post_get.py::test_post_get PASSED                                        [ 85%]
test_post_get.py::test_get_nonexistent PASSED                                 [ 90%]
test_validation.py::test_valid PASSED                                         [ 95%]
test_validation.py::test_invalid PASSED                                       [100%]

================================ 20 passed in 42.44s ================================
```

## Deploy

Systemd service files are located in the [`deployment`](deployment)
