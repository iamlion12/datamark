# -*- coding: utf-8 -*-

@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki()

def user():
    return dict(form=auth())

@auth.requires_membership('admin')
def refresh():

    import os

    Files = os.listdir('applications/datamark/static/unchecked_images/')

    for name in Files:
        db.image_list.insert(name=name)

    state = "Succseed!"

    return dict(state=state)

def mark():

    import os

    if db(db.image_list).select(limitby=(0,1)):
        img_name = db().select(db.image_list.ALL, orderby='<random>', limitby=(0,1))[0].name

        class1_button = FORM(INPUT(_type='submit', _value='Первый класс'), _action=URL('submit_mark', vars=dict(img_name=img_name, mark=0)))
        class2_button = FORM(INPUT(_type='submit', _value='Второй класс'), _action=URL('submit_mark', vars=dict(img_name=img_name, mark=1)))
        skip_button = FORM(INPUT(_type='submit', _value='Пропустить'), _action=URL('submit_mark', vars=dict(img_name=img_name, mark=2)))

        return dict(img_name = img_name, class1_button = class1_button, class2_button = class2_button, skip_button = skip_button)

    else:
        redirect(URL('null'))

def submit_mark():
    import os
    db.dataset.insert(name=request.vars.img_name, mark=request.vars.mark)
    try:
        os.rename(os.path.join(request.folder, 'static','unchecked_images', request.vars.img_name),
                  os.path.join(request.folder, 'static','checked_images', request.vars.img_name))
        
    except FileNotFoundError:
        db(db.image_list.name == request.vars.img_name).delete()
        redirect(URL('mark'))

    db(db.image_list.name == request.vars.img_name).delete()
    redirect(URL('mark'))
    return dict()


def null():
    state = "All work is done. Relax."
    return dict(state=state)

@cache.action()
def download():
    return response.download(request, db)
