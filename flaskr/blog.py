from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from datetime import timezone, datetime, timedelta
import pytz
from flaskr.auth import login_required
from flaskr.db import get_db
import urllib.request, json 
from flask import session
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname, realpath
import uuid

bp = Blueprint("blog", __name__)

@bp.route("/")
def index():
    posts=""

    if g.user:
        user=g.user['id']
        db = get_db()
        posts = db.execute(
            "SELECT id, title, body, created, author_id, img_url"
            " FROM post "
            " WHERE author_id = ? "
            " ORDER BY created DESC"
            " LIMIT 5"
            ,(user,)
        ).fetchall()
        following = db.execute(
            "SELECT *"
            " FROM follow f JOIN post p ON p.author_id=f.follows_id"
            " JOIN user u ON p.author_id=u.id"
            " WHERE f.user_id = ? "
            " ORDER BY created DESC"
            ,(user,)
        ).fetchall()
        followers = db.execute(
            "SELECT DISTINCT *"
            " FROM follow f JOIN user u ON f.user_id=u.id"
            " WHERE follows_id = ? ",
            (user,),
            ).fetchall()
        pop=round(popularity(user),2)
        # check new updates from likes, followers, comments
        time=datetime.now(pytz.timezone('America/New_York'))
        
        return render_template("blog/index.html",posts=posts, following=following, followers=followers,pop=pop)
    return render_template("blog/index.html")


@bp.route("/<int:id>/profile", methods=("POST","GET"))
@login_required
def profile(id):
    db = get_db()
    c_user=g.user['id']
    followed=False
    msg=""
    user = db.execute(
                "SELECT *"
                " FROM user "
                " WHERE user.id =?", 
                (id,),
                ).fetchone()
    posts=db.execute(
                 "SELECT p.id, title, body, created, img_url, author_id, nickname,username"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE u.id=? "
                " ORDER BY created DESC", 
                (id,),
                ).fetchall()
    following = db.execute(
            "SELECT DISTINCT *"
            " FROM follow f JOIN user u ON f.follows_id=u.id"
            " WHERE user_id = ? ",
            (id,),
            ).fetchall()
    followers = db.execute(
            "SELECT DISTINCT *"
            " FROM follow f JOIN user u ON f.user_id=u.id"
            " WHERE follows_id = ? ",
            (id,),
            ).fetchall()
    check=db.execute(
            "SELECT  *"
            " FROM follow "
            " WHERE user_id = ? AND follows_id = ? ",
            (c_user,id,),
            ).fetchall()
    if len(check)!=0:
        followed=True
    # check a user's popularity
    pop=round(popularity(id),2)
    if len(user)==0:
        msg="no such a user, please try again."
    else:
        return render_template("blog/profile.html",user=user,posts=posts, followers=followers, msg=msg, following=following,followed=followed,pop=pop)

def popularity(id):
    pop=0
    db = get_db()
    posts=db.execute(
                 "SELECT *"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE u.id=? ", 
                (id,),
                ).fetchall()
    followers = db.execute(
            "SELECT DISTINCT *"
            " FROM follow f JOIN user u ON f.user_id=u.id"
            " WHERE follows_id = ? ",
            (id,),
            ).fetchall()
    likes = db.execute(
            "SELECT *"
            " FROM post p JOIN likes l ON p.id=l.post_id"
            " JOIN user u ON p.author_id=u.id"
            " WHERE p.author_id = ? ", 
            (id,),
            ).fetchall()
   
    # totalposts=len(db.execute("SELECT * FROM post").fetchall())
    # totalusers=len(db.execute("SELECT * FROM user WHERE NOT user_type='admin' ").fetchall())
    # totallikes=len(db.execute('SELECT * FROM likes').fetchall())
    points=(len(posts))*2
    points=points+(len(followers))*5
    points=points+(len(likes))*3


    # compute the ranking by pandas' map function
    # con=get_con()
    # df = pd.read_sql_query("SELECT * FROM ranks", con)
    # con.close()
    # print(df.head())
    # result=pd.cut(df['rank'],bins=100)


    if(db.execute("SELECT * FROM ranks WHERE user_id=?",(id,)).fetchone()):
        db.execute("UPDATE ranks SET points=? WHERE user_id=?",(points,id,))
        db.commit()
    else:
        db.execute("INSERT INTO ranks (user_id,points) VALUES(?,?)",(id,points,))
        db.commit()

    totalranks=db.execute("SELECT * FROM ranks ").fetchall()
    print(points)
    sum=[]
    max=0
    min=100
    for i in range(len(totalranks)):
        sum.append(totalranks[i]['points'])
        if totalranks[i]['points']>max:
            max=totalranks[i]['points']
        if totalranks[i]['points']<min:
            min=totalranks[i]['points']
    s=(max-min)/100
    if s==0:
        s=1
    for i in range(len(totalranks)):
        r=(totalranks[i]['points']-min)/s+1
        print(r)
        db.execute("UPDATE ranks SET rank=? WHERE user_id=?",(r,totalranks[i]['user_id'],))
        db.commit()

    rank=db.execute("SELECT * FROM ranks WHERE user_id=?",(id,)).fetchone()['rank']
    print(rank)
    return rank



@bp.route("/<int:offset>/posts", methods=("GET", "POST"))
@login_required
def posts(offset):
    """Show all the posts, most recent first."""
    # print(offset)
    search = False
    q = request.args.get('q')
    if q:
        search = True
    # grab all posts in site
    db = get_db()
    count=len(db.execute("SELECT * FROM post").fetchall())
    posts = db.execute(
        "SELECT *"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
        " LIMIT 50"
        " OFFSET ?",(offset,)
    ).fetchall()
   
    return render_template("blog/posts.html", posts=posts)

# @bp.route("/api",methods=("GET","POST"))
# @login_required
# def api():
#   # flickr api onload
#     tag='cats'
#     if request.method == "POST":
#         searchflickr=request.form['searchflickr']
#         print(searchflickr)
#         tag=searchflickr
#     print(tag)
#     with urllib.request.urlopen("https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=eb884d8dd3938fa40910decb88bbd9ad&tags="+tag+"&format=json&nojsoncallback=1&api_sig=2a338fed2b0cd07377a7f7127b518e8c") as url:
#         data = json.loads(url.read().decode())
#         photos=data['photos']['photo']
#     for photo in photos:
#         photo['url']='http://farm'+str(photo['farm'])+'.staticflickr.com/'+photo['server']+'/'+photo['id']+'_'+photo['secret']+'.jpg'
#     return render_template("blog/ins.html", photos=photos)   


@bp.route("/<int:id>/<int:dir>/post", methods=("GET", "POST"))
@login_required
def post(id,dir):
    """Show the post details"""
    user_id = session.get("user_id")
    db = get_db()
    # count=len(db.execute("SELECT * FROM post").fetchall())
    max=db.execute("SELECT MAX(id) FROM post").fetchone()['MAX(id)']
    
    post1 = db.execute(
        "SELECT p.id, title, body, created, img_url, author_id, pfp, nickname,username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ? ", 
        (id,),
        ).fetchone()
    likes = db.execute(
        "SELECT *"
        " FROM post p JOIN likes l ON p.id=l.post_id"
        " WHERE p.id = ? ", 
        (id,),
        ).fetchall()
    while post1 is None: #if cant find the post id(maybe it's deleted or out of range)
        if id>max or id<1: #if it is out of range:
            return render_template("blog/nopost.html")
        #if it is deleted, loop until find next one in the direction
        elif dir==2: #2: go back 
            id=id-1
        elif dir==1:#1: go next
            id=id+1
        post1 = db.execute(
            "SELECT p.id, title, body, created, img_url, author_id, nickname,username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ? ", 
            (id,),
            ).fetchone()    
        likes = db.execute(
            "SELECT *"
            " FROM post p JOIN likes l ON p.id=l.post_id"
            " WHERE p.id = ? ", 
            (id,),
            ).fetchall()


    # commentcount=len(db.execute("SELECT * FROM post").fetchall())
    
    comments = db.execute(
        "SELECT c.id, c.post_id,c.body, c.created, c.author_id, c.retweet_id,u.username,u.nickname"
        " FROM comments c "
        " LEFT JOIN post p ON c.post_id = p.id"
        " LEFT JOIN user u ON c.author_id = u.id"
        " WHERE c.post_id = ? ORDER BY c.created DESC", 
        (id,),
        ).fetchall()
    liked=False
    check = db.execute(
           " SELECT * FROM likes WHERE user_id = ? AND post_id = ?", (user_id ,id,),
        ).fetchone()
    if check:
        liked=True
    return render_template("blog/post.html", post=post1,comments=comments,liked=liked,likes=likes)



    
    
@bp.route("/<int:id>/like", methods=("GET", "POST"))
@login_required
def like(id):
    """follow another user"""
    user_id = session.get("user_id")
    if request.method == "POST":
        db = get_db()
        # current user (user_id) follows profile user (id)
        check = db.execute(
           " SELECT * FROM likes WHERE user_id = ? AND post_id = ?", (user_id ,id,),
        ).fetchone()
        if not check:
            db.execute(
                "INSERT INTO likes (user_id, post_id) VALUES (?, ?) ",(user_id ,id,),
            )
            db.commit()
        return redirect(url_for("blog.post",id=id,dir=0))

@bp.route("/<int:id>/unlike", methods=("GET", "POST"))
@login_required
def unlike(id):
    """follow another user"""
    user_id = session.get("user_id")
    if request.method == "POST":
        db = get_db()
        # current user (user_id) follows profile user (id)
        # delete this relationship
        check = db.execute(
           " SELECT * FROM likes WHERE user_id = ? AND post_id = ?", (user_id ,id,),
        ).fetchone()
        if check:
            db.execute(
                "DELETE FROM likes WHERE user_id=? AND post_id=? ",(user_id ,id,),
            )
            db.commit()
        return redirect(url_for("blog.post",id=id,dir=0))





    
@bp.route("/<int:id>/<int:user>/comment", methods=("GET", "POST"))
@login_required
def comment(id,user):
    #get current time stamp and convert to new york time
    time=datetime.now(pytz.timezone('America/New_York'))
    """Create a new comment for the current user."""
    if request.method == "POST":
        body = request.form["commentbody"]
        error = None
    if error is not None:
        flash(error)
    if not body:
            error = "context is required."
    else:
        db = get_db()
        db.execute(
            "INSERT INTO comments (post_id, body, author_id,created) VALUES (?, ?, ?,?)",
            (id, body, user,time),
        )
        db.commit()
        
    return  redirect(url_for("blog.post",id=id,dir=0))

@bp.route("/<int:id>/<int:user>/<int:cid>/commentupdate", methods=("GET", "POST"))
@login_required
def commentupdate(id,user,cid):
    #get current time stamp and convert to new york time
    time=datetime.now(pytz.timezone('America/New_York'))
    """update the comment."""
    if request.method == "POST":
        body = request.form["commentbodyup"]
        error = None
    if error is not None:
        flash(error)
    if not body:
            error = "context is required."
    else:
        db = get_db()
        db.execute(
            "UPDATE comments SET body=?, created=? WHERE id=? AND post_id=? ",
            (body,time, cid,id),
        )
        db.commit()
    return  redirect(url_for("blog.post",id=id,dir=0))




@bp.route("/<int:id>/<int:cid>/commentdelete", methods=("POST",))
@login_required
def commentdelete(id,cid):
    """Delete a comment.

    """
   
    db = get_db()
    db.execute("DELETE FROM comments WHERE id = ?", (cid,))
    # print("DELETE FROM comments WHERE id = ?", (cid,))
    db.commit()
    return redirect(url_for("blog.post",id=id,dir=0))

@bp.route("/<int:id>/<int:user>/<int:rid>/commentretweet", methods=("GET", "POST"))
@login_required
def commentretweet(id,user,rid):
    #get current time stamp and convert to new york time
    time=datetime.now(pytz.timezone('America/New_York'))
    """Create a new comment for the current user."""
    if request.method == "POST":
        body = request.form["commentboxretweet"]
        error = None
    if error is not None:
        flash(error)
    if not body:
            error = "context is required."
    else:
        db = get_db()
        db.execute(
            "INSERT INTO comments (post_id, body, author_id,created,retweet_id) VALUES (?, ?, ?,?,?)",
            (id, body, user,time,rid),
        )
        db.commit()
     
    return  redirect(url_for("blog.post",id=id,dir=0))

@bp.route("/<int:id>/<int:cid>/admincommentdelete", methods=("POST",))
@login_required
def admincommentdelete(id,cid):
    """Delete a comment as admin
    """
    db = get_db()
    db.execute("DELETE FROM comments WHERE id = ?", (cid,))
    # print("DELETE FROM comments WHERE id = ?", (cid,))
    db.commit()
    return redirect(url_for("blog.post",id=id,dir=0))



def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, img_url, author_id, username,nickname"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post

UPLOAD_FOLDER = './static/upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    user_id = session.get("user_id")
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        # img_url = request.form["img_url"]
        error = None
         #get current time stamp and convert to new york time
        time=datetime.now(pytz.timezone('America/New_York'))
        if not title:
            error = "Title is required."

        img_url="#"
        if 'file' not in request.files:
            flash('No file part')
            print('No file part')
            # return render_template("auth/edit.html")
        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                print('No selected file')
                return render_template("auth/edit.html")
            if file and allowed_file(file.filename):
                filename = secure_filename(str(user_id)+"-"+str(uuid.uuid4())+"-"+str(time)+file.filename)
                # file.save(os.path.join(UPLOAD_FOLDER, filename))
                UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/upload/post')
                file.save(os.path.join(UPLOADS_PATH, filename))
                img_url='/static/upload/post/'+filename

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, img_url, author_id,created) VALUES (?, ?, ?, ?,?)",
                (title, body, img_url, g.user["id"],time),
            )
            db.commit()
            return redirect(url_for("blog.posts",id=id,dir=0,offset=0))

    return render_template("blog/create.html")

# delete post
@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.posts",offset=0))

# update post
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)
    user_id = session.get("user_id")
    time=datetime.now(pytz.timezone('America/New_York'))
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        # img_url = request.form["img_url"]
        error = None
        db = get_db()
        img_url=db.execute("SELECT img_url FROM post WHERE id=?",(id,)).fetchone()[0]
        if 'file' not in request.files:
            flash('No file part')
            print('No file part')
            # return render_template("auth/edit.html")
        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                print('No selected file')
                return render_template("auth/edit.html")
            if file and allowed_file(file.filename):
                filename = secure_filename(str(user_id)+"-"+str(uuid.uuid4())+"-"+str(time)+file.filename)
                # file.save(os.path.join(UPLOAD_FOLDER, filename))
                UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/upload/post')
                file.save(os.path.join(UPLOADS_PATH, filename))
                img_url='/static/upload/post/'+filename

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            
            db.execute(
                "UPDATE post SET title = ?, body = ?, img_url=? WHERE id = ?", (title, body,img_url, id)
            )
            db.commit()
            return redirect(url_for("blog.post",id=id,dir=0))

    return render_template("blog/update.html", post=post)

@bp.route("/search", methods=("POST","GET"))
@login_required
def search():
    
    """return the result of list of users and posts
    """
    msg={'post':"",'users':""}
    if request.method == "POST":
        body=request.form["searchbody"]
        text = "%"+request.form["searchbody"].lower()+"%"

        error = None
        if error is not None:
            flash(error)
        if not body:
            error = "context is required."
        else:
            db = get_db()
  
            posts = db.execute(
                "SELECT p.id, title, body, created, img_url, author_id, username,nickname"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE title LIKE ? ", 
                (text,),
                ).fetchall()
            users = db.execute(
                "SELECT *"
                " FROM user"
                " WHERE nickname LIKE ? AND user_type='user'", 
                (text,),
                ).fetchall()
            
            if len(posts) ==0: #if cant find the post id(maybe it's deleted or out of range)
                msg['posts']="No result from posts"
            if len(users) ==0:
                msg['users']="No result from users"
            return render_template("blog/result.html",posts=posts, users=users,word=body,msg=msg)
    return render_template("blog/search.html")

@bp.route("/api")
@login_required
def api():
    return render_template("API/index.html")
