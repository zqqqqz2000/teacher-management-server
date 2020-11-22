from flask import Flask
from flask import request
from flask_cors import CORS
import datetime
from dao.check import Check
from dao.finance_office import FinanceOffice
from dao.salary import Salary
from dao.submission import Submission
from dao.teacher import Teacher
from global_var import db
from utils.token import with_token, tokenize
from dao.hr_office import HROffice
from dao.department import Department
from utils.enc import md5
import config
from typing import *

app = Flask(__name__)
app.config.from_object(config)
CORS(app, resources=r'/*', supports_credentials=True)
with app.app_context():
    db.init_app(app=app)
    # db.drop_all()
    db.create_all()


@app.route('/hrlogin', methods=['POST'])
def hrlogin():
    data = request.get_json(silent=True)
    username = data['username']
    password = data['password']
    pass_hash = md5(password)
    query_res = HROffice.query.filter_by(
        username=username,
        password=pass_hash
    ).first()
    if query_res:
        return {'success': True, 'token': tokenize({'username': username})}
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


@app.route('/add_department', methods=['POST'])
@with_token
def add_department(token: Dict):
    data = request.get_json(silent=True)
    department_name = data['name']
    if token:
        d = Department(name=department_name)
        db.session.add(d)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False, 'info': '请先登录'}


@app.route('/get_department', methods=['POST'])
@with_token
def get_department(token: Dict):
    data = request.get_json(silent=True)
    if token:
        ds: List[Department] = Department.query.all()
        res = [{
            'id': d.id,
            'name': d.name
        } for d in ds]
        return {'success': True, 'departments': res}
    else:
        return {'success': False, 'info': '请先登录'}


@app.route('/del_department', methods=['POST'])
@with_token
def del_department(token: Dict):
    data = request.get_json(silent=True)
    if token:
        id_ = data['id']
        d = Department.query.filter_by(id=id_).first()
        db.session.delete(d)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False, 'info': '请先登录'}


# 教师
@app.route('/add_teacher', methods=['POST'])
@with_token
def add_teacher(token: Dict):
    data = request.get_json(silent=True)
    if token:
        del data['token']
        data['password'] = md5(data['password'])
        t = Teacher(
            **data
        )
        db.session.add(t)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False, 'info': '请先登录'}


@app.route('/get_teacher', methods=['POST'])
@with_token
def get_teacher(token: Dict):
    data = request.get_json(silent=True)
    if token:
        ts: List[Tuple[Teacher, str]] = db.session.query(Teacher, Department.name).join(Department).all()
        res = [{
            'id': t.id,
            'name': t.name,
            'username': t.username,
            'age': t.age,
            'department': dname,
            'gender': '男' if t.gender else '女',
            'education': t.education,
            'title': t.title,
            'marry': '已婚' if t.marry else '未婚',
            'hiredate': str(t.hiredate),
            'status': '未在职' if t.status else '在职'
        } for t, dname in ts]
        return {'success': True, 'teacher': res}
    else:
        return {'success': False, 'info': '请先登录'}


@app.route('/teacher_check', methods=['POST'])
@with_token
def teacher_check(token: Dict):
    data = request.get_json(silent=True)
    if token:
        teachers = data['teachers']
        for t in teachers:
            tid = t['id']
            date = t['date']
            check = t['check']
            c = Check(
                tid=tid,
                date=datetime.datetime.strptime(date, '%Y-%M-%d').date(),
                check=check
            )
            db.session.add(c)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False, 'info': '请先登录'}


@app.route('/submission', methods=['POST'])
@with_token
def submission(token: Dict):
    data = request.get_json(silent=True)
    if token:
        from_, to = data['range']
        checks = db.session.query(Teacher.name, Check.tid, db.func.count('*').label('c')).filter(
            Check.date >= from_,
            Check.date <= to,
            Check.check == 0,
            Teacher.id == Check.tid
        ).group_by(Check.tid).all()
        basic_salary = data['basic_salary']
        bonus = data['bonus']
        tax = data['tax']
        comment = data['comment']
        for _, tid, times in checks:
            s = Submission(
                tid=tid,
                check_fine=50 * int(times),
                basic_salary=basic_salary,
                bonus=bonus,
                tax=tax,
                comment=comment,
                date=datetime.datetime.now().date()
            )
            db.session.add(s)
        db.session.commit()
        check_status = [f'教师: {name}，签到漏签{times}次' for name, tid, times in checks]
        return {'success': True, 'info': check_status}
    else:
        return {'success': False, 'info': '请先登录'}


# 财务处
@app.route('/get_submission', methods=['POST'])
@with_token
def get_submission(token: Dict):
    data = request.get_json(silent=True)
    if token:
        subs: List[Tuple[str, Submission]] = db.session.query(Teacher.name, Submission).filter(
            Teacher.id == Submission.tid
        ).all()
        res = [{
            'id': sub.id,
            'name': name,
            'check_fine': sub.check_fine,
            'basic_salary': sub.basic_salary,
            'tax': sub.tax,
            'comment': sub.comment,
            'date': str(sub.date),
            'approve': '已审批' if sub.approve else '未审批'
        } for name, sub in subs]
        return {'success': True, 'submissions': res}
    else:
        return {'success': False}


@app.route('/finance_login', methods=['POST'])
def finance_login():
    data = request.get_json(silent=True)
    username = data['username']
    password = data['password']
    pass_hash = md5(password)
    query_res = FinanceOffice.query.filter_by(
        username=username,
        password=pass_hash
    ).first()
    if query_res:
        return {'success': True, 'token': tokenize({'username': username})}
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


@app.route('/delete_submission', methods=['POST'])
@with_token
def delete_submission(token: Dict):
    data = request.get_json(silent=True)
    if token:
        id_ = data['id']
        s = Submission.query.filter_by(id=id_).first()
        db.session.delete(s)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


@app.route('/approve_submission', methods=['POST'])
@with_token
def approve_submission(token: Dict):
    data = request.get_json(silent=True)
    if token:
        id_ = data['id']
        s: Submission = Submission.query.filter_by(id=id_).first()
        s.approve = 1
        salary = Salary(
            tid=s.tid,
            check_fine=s.check_fine,
            basic_salary=s.basic_salary,
            bonus=s.bonus,
            tax=s.tax,
            date=s.date,
            comment=s.comment
        )
        db.session.add(salary)
        db.session.commit()
        return {'success': True}
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


# 教师登录
@app.route('/teacher_login', methods=['POST'])
def teacher_login():
    data = request.get_json(silent=True)
    username = data['username']
    password = data['password']
    pass_hash = md5(password)
    query_res = Teacher.query.filter_by(
        username=username,
        password=pass_hash
    ).first()
    if query_res:
        return {'success': True, 'token': tokenize({'username': username})}
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


@app.route('/teacher_info', methods=['POST'])
@with_token
def teacher_info(token: Dict):
    data = request.get_json(silent=True)
    if token:
        username = token['username']
        checks: List[Check] = db.session.query(Check).filter(
            Teacher.username == username,
            Check.tid == Teacher.id
        ).all()
        salary: List[Salary] = db.session.query(Salary).filter(
            Salary.tid == Teacher.id,
            Teacher.username == username
        ).all()
        teachers: List[str, Teacher] = db.session.query(Department.name, Teacher).filter(
            Teacher.username == username
        )
        return {'success': True, 'infos': {
            'checks': [{
                'id': check.id,
                'date': str(check.date),
                'check': '已签到' if check.check else '未签到'
            } for check in checks],
            'salary': [{
                'id': s.id,
                'check_fine': s.check_fine,
                'basic_salary': s.basic_salary,
                'bonus': s.bonus,
                'tax': s.tax,
                'date': str(s.date),
                'comment': s.comment
            } for s in salary],
            'teachers': [{
                'id': teacher.id,
                'name': teacher.name,
                'username': teacher.username,
                'education': teacher.education,
                'age': teacher.age,
                'title': teacher.title,
                'marry': '未婚' if teacher.marry else '已婚',
                'department': department_name,
                'hiredate': str(teacher.hiredate),
                'status': '在职' if teacher.status else '离职'
            } for department_name, teacher in teachers]
        }}
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


@app.route('/searcher', methods=['POST'])
@with_token
def searcher(token: Dict):
    data = request.get_json(silent=True)
    if token:
        del data['token']
        data = {k: v for k, v in data.items() if v}
        teachers: List[str, Teacher] = db.session.query(Teacher, Department).filter_by(
            **data
        ).join(Department).all()
        print(teachers)

        return {'success': True, 'teachers': [{
            'id': teacher.id,
            'name': teacher.name,
            'username': teacher.username,
            'education': teacher.education,
            'age': teacher.age,
            'title': teacher.title,
            'marry': '未婚' if teacher.marry else '已婚',
            'department': department.name,
            'hiredate': str(teacher.hiredate),
            'status': '在职' if teacher.status else '离职'
        } for teacher, department in teachers]}
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


@app.route('/dis', methods=['POST'])
@with_token
def dis(token: Dict):
    data = request.get_json(silent=True)
    if token:
        id_ = data['id']
        t: Teacher = Teacher.query.filter_by(id=id_).first()
        t.status
    else:
        return {'success': False, 'info': '请核对用户名和密码'}


if __name__ == '__main__':
    app.run()
