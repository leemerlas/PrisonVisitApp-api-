from prisonapp import *
from models import User, Comment, Visitation


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])

            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# START OF VISITOR API

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password_hash=hashed_password,
                    firstname=data['firstname'], middlename=data['middlename'],
                    lastname=data['lastname'], contact=data['contact'], address=data['address'],
                    birthday=data['birthday'], prisoner=data['prisoner'], role_id=2, status=True,
                    age=data['age'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registered successfully!'})


@app.route('/api/login/', methods=['GET'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    if check_password_hash(user.password_hash, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'])

        print 'Token generated!'
        return jsonify(
            {'status': 'ok', 'token': token.decode('UTF-8'), 'role_id': user.role_id, 'public_id': user.public_id,
             'message': 'login successful!'})


@app.route('/api/user/visitation', methods=['POST'])
@token_required
def visitation(current_user):
    data = request.get_json()
    user = User.query.filter_by(public_id=data['public_id']).first()

    new_visit = Visitation(vId=int(user.id), nameP=data['nameP'], date=data['vDate'],
                           numberOfVisitors=int(data['numV']), status='PENDING', time=data['timeV'],
                           relationship=data['relation'])
    db.session.add(new_visit)
    db.session.commit()

    return jsonify({'message': 'Success!'})


@app.route('/api/user/comment', methods=['POST'])
@token_required
def post_comment(current_user):
    data = request.get_json()
    get_id = User.query.filter_by(public_id=data['public_id']).first()

    new_comment = Comment(uid=int(get_id.id), content=data['comment'])
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment submitted! Thank you for your opinion!'})


# END OF VISITOR API


# START OF CLERK API


# END OF CLERK API
