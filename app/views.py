from urllib import unquote
from flask import render_template, redirect, url_for, request,Response,abort
from flask.ext.paginate import Pagination
from tools import *
from app import app, mongo, recaptcha
from constants import NEWS_ON_PAGE, NEWS_ON_PAGE_RANDOM, PATH_TO_GUIDES, PATH_TO_BANNERS, ONLINE_KEY_API
from forms import RegisterForm, LoginForm, FreeForm, ContactForm
from models import News, User, Free, Contact
from urllib import quote, unquote
from flask.ext.paginate import Pagination
from random import choice
from datetime import timedelta, datetime
import os
from user_online import mark_online,get_online_users

@app.before_request
def mark_current_user_online():
    mark_online(request.remote_addr)

@app.route('/online/<key>')
def online(key):
    if key == ONLINE_KEY_API:
        return Response('%d|%s' % (get_online_users(),request.remote_addr),
                        mimetype='text/plain')
    abort(404)

@app.route('/')
@app.route('/home')
@app.route('/news/page/<page>')
def index(page=1):
    print page
    page = int(page)
    count_news = News.objects().count()
    posts = News.objects.order_by('-date').skip((page - 1) * NEWS_ON_PAGE).limit(NEWS_ON_PAGE)
    pagination = Pagination(page=page,
                            per_page=NEWS_ON_PAGE,
                            total=count_news,
                            record_name='News',
                            format_total=True, format_number=True)
    return render_template("news.html", posts=posts, pagination=pagination, title="Cryptocurrency news today")

    
@app.route('/search')
def search():
    import re
    def validate(find):
        if not find:
            return False
        if not len(find) > 3 and len(find) < 40:
            return False
        if not re.match(re.compile('^[a-zA-Z]+([-_ ]?[a-zA-Z0-9]+){0,2}$'), find):
            return False
        return True

    find = request.args['search']
    page = int(request.args['page']) if 'page' in request.args else 1

    if not validate(find):
        return redirect('/')

    find = find.split()
    word = find.pop(0)
    posts = list(mongo.db.news.find({'$or': [ { 'title':  {"$regex": word, "$options": "-i"} }, { 'text': {"$regex": word, "$options": "-i"} }]}))
    while find:
        regx = re.compile(find.pop(0), re.IGNORECASE)
        i = len(posts)
        while i > 0:
            i -= 1
            if not re.search(regx, posts[i]['title']) and not re.search(regx, posts[i]['text']):
                posts.pop(i)
    count_news = len(posts)
    skip = (page - 1) * NEWS_ON_PAGE
    limit = skip + NEWS_ON_PAGE
    posts = posts[skip:limit]
    pagination = Pagination(page=page,
                            per_page=NEWS_ON_PAGE,
                            total=count_news,
                            record_name='News',
                            format_total=True, format_number=True)
    return render_template("news.html", posts=posts, pagination=pagination, title="Results")
    
    
@app.route('/tags/<tag>')
@app.route('/tags/<tag>/<page>')
def tags(tag, page=1):
    page = int(page)
    count_news = News.objects(category=tag).count()
    posts = News.objects(category=tag).order_by('-date').skip((page - 1) * NEWS_ON_PAGE).limit(NEWS_ON_PAGE)
    pagination = Pagination(page=page,
                            per_page=NEWS_ON_PAGE,
                            total=count_news,
                            record_name='News',
                            format_total=True, format_number=True)
    return render_template("news.html", posts=posts, pagination=pagination, title="Cryptocurrency news today")


@app.route('/news/<link>')
def news(link):
    news = News.objects(link=unquote(link)).first()
    news.popular = news.popular + 1 if news.popular else 1
    news.save()
    return render_template("single_news.html", news=news, title=news['title'])


@app.route('/signin', methods=('GET', 'POST'))
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        print "ok"
        return redirect(url_for('index'))
    return render_template("login.html", form=form, login_tmp=True)


@app.route('/signup', methods=('GET', 'POST'))
def signup():
    form = RegisterForm()
    print 'er', form.errors
    if form.validate_on_submit():
        User(login=form.login.data, password=form.password.data, email=form.email.data,
             bitcoin_wallet=form.bitcoin_wallet.data).save()
        return redirect('/signup')
    return render_template('register.html', form=form)


@app.route('/free_bitcoin', methods=['GET', 'POST'])
def free_bitcoin():
    render_word = {}
    render_word['time_left'] = None
    render_word['username'] = request.cookies.get('username') if request.cookies.get('username') else ""
    render_word['info_text'] = 'Check balance: <a href="https://faucetbox.com/en/check/' + render_word[
        'username'] + '">link</a>' if render_word['username'] else ""
    render_word['all_balance'] = mongo.db.balance.find_one({})['balance']
    ip = request.remote_addr
    reffer = request.args['ref'] if 'ref' in request.args else None
    form = FreeForm()
    user_data = Free.objects(ip=ip).order_by('-date').limit(1).first()
    if user_data:
        time_left = check_time(user_data)
        render_word['reward'] = user_data['reward']
        if time_left:
            render_word['time_left'] = time_left

            return render_template("free_bitcoin.html", **render_word)
    if form.validate_on_submit()  and recaptcha.verify():
        user_data = Free.objects(wallet=form.wallet.data).order_by('-date').limit(1).first()
        if user_data:
            time_left = check_time(user_data)
            if time_left:
                render_word['time_left'] = time_left
                render_word[
                    'info_text'] = 'Check balance: <a href="https://faucetbox.com/en/check/' + form.wallet.data + '">link</a>' + "<br>Your wallet is used, pls wait 1440 min"
                print form.wallet.data
                return render_template("free_bitcoin.html", **render_word)
        if 'collect' in request.form:
            coin = 300
        elif 'try' in request.form:
            coin = choice([100,200,600])
        send_status = send_money(form.wallet.data, coin, reffer)
        render_word['coin'] = coin
        if send_status[0]:
            Free(wallet=form.wallet.data, ip=ip, reward=coin, reffer=reffer).save()
            response = app.make_response(redirect('/free_bitcoin'))
            response.set_cookie('username', value=form.wallet.data)
            print 'OK'
            return response
        else:
            render_word['info_text'] = "Server error"

    return render_template("free_bitcoin.html", form=form, **render_word)


@app.context_processor
def utility_processor():
    def get_tags():
        word_ = News._get_collection().aggregate([
            {"$project": {"category": 1}},
            {"$unwind": "$category"},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ])
        list_ = []
        for el in word_['result']:
            if el['_id'] == 'News':
                break;
            list_.append({'text': el['_id'], 'weight': el['count'], 'link': "/tags/" + el['_id']})
        return list_

    def get_random_news():
        news_list = News.objects.order_by('-popular').limit(NEWS_ON_PAGE_RANDOM)
        return news_list

    def login_form():
        return LoginForm()    
        
    def get_banner(id):
        f = open(PATH_TO_BANNERS+'/'+str(id)+'.txt')
        data = f.read()
        f.close()
        return data

    return dict(get_tags=get_tags, get_random_news=get_random_news, login_form=login_form, get_banner=get_banner)


@app.route('/guides/<name>')
def guides(name):
    title = name.replace("-", " ")
    if title:
        title = title[0].upper() + title[1:]
    return render_template('guides/{0}.html'.format(name), title=title)


@app.route('/bitcoin_price')
def price():
    return render_template('bitcoin_price.html', title="Price")


@app.route('/contact_us', methods=('GET', 'POST'))
def contact_us():
    return render_template('contact_page.html')


@app.route('/contact_us_frame', methods=('GET', 'POST'))
def contact_us_frame():
    form = ContactForm()
    print 'er', form.errors
    if form.validate_on_submit():
        Contact(name=form.name.data, email=form.email.data, message=form.message.data).save()
        form.name.data = ""
        form.email.data = ""
        form.message.data = ""
        return render_template('contact_us.html', form=form,
                               success_info='<span style="color: green;">Your message has been successfully sent. <img src="/images/ok-icon.png" /> </span>')
    return render_template('contact_us.html', form=form)


@app.route('/sitemap.xml')
def sitemap():
    pages = []
    ten_days_ago = datetime.now().date().isoformat()
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            pages.append(
                [rule.rule, ten_days_ago]
            )
    for news in News.objects():
        pages.append(['/news/' + news.link, news.date.date().isoformat()])
    for el in os.listdir(PATH_TO_GUIDES):
        pages.append(
            ['/guides/' + el.split('.')[0], ten_days_ago]
        )
    url_root = "http://cryptocoiners.net"
    sitemap_xml = render_template('sitemap.xml', pages=pages, url_root=url_root)
    response = app.make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
