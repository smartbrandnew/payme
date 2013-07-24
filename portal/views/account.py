# -*- coding: utf-8 -*-
"""
The account views are here.
"""
import time
import logging
import random
import urllib

from django.views import generic


from DjangoVerifyCode import Code

from portal import forms
from portal import models
from portal.views import utils
from portal.views.base import require_auth
from portal.views.base import sendmessage

LOG = logging.getLogger(__name__)


@require_auth
def home(request):
    return utils.render('account/home.html', {})


@require_auth
def verifycode(request):
    code = Code(request)
    code.worlds = ['hello', 'world', 'helloworld']
    code.type = 'number'
    return code.display()


@require_auth
def vip(request):
    return utils.render('account/vip.html', {})


@require_auth
def account_chargeent_list(request):
    user = utils.get_user_obj(request)
    charge_rents = user.landlordrentprofile_set.all()
    return utils.render('account/chargerentlist.html',
                        {'charge_rents': charge_rents})


@require_auth
def account_payrent_list(request):
    user = utils.get_user_obj(request)

    renters = []
    passive_renters = user.landlordrenterinfo_set.all()
    active_renters = user.renterrentprofile_set.all()

    renters.extend(passive_renters)
    renters.extend(active_renters)
    renters.sort(key=lambda x: x.created_at)
    renters.reverse()
    return utils.render('account/payrentlist.html',
                        {'renters': renters})
    user = utils.get_user_obj(request)

    if user.is_vip == False:
        return vipconfirm(request)
    else:
        return utils.render('account/vip.html', {'message': 'Welcome,VIP!'})


class Vipconfirm(generic.FormView):
    template_name = 'portal/account/vipconfirm.html'
    form_class = forms.VipForm

    def form_valid(self, form):
        user = utils.get_user_obj(self.request)
        data = form.cleaned_data
        if models.Vip.objects.filter(text=data['text']):
            user.is_vip = True
            user.save()
            content = 'You have been VIP client!'
            sendmessage(self.request, content)
            return vip(self.request)

vipconfirm = Vipconfirm.as_view()


@require_auth
def info(req):
    usernam = req.session.get('username')
    user = models.User.objects.filter(username=usernam)
    return utils.render('personal_info.html',
                        {'username': user[0].username,
                         'phone': user[0].phone,
                         'real_id': user[0].real_id,
                         'real_name': user[0].real_name,
                         'email': user[0].email})


@require_auth
def cardmanage(request):
    user = utils.get_user_obj(request)
    #user_id = user.id
    #cards = BankCard.objects.filter(owner_id = user_id)
    cards = user.bankcard_set.all()
    return utils.render('account/bankcards.html', {'cards': cards})


def safe(req):
    usernam = req.session.get('username')
    user = models.User.objects.filter(username=usernam)
    local_time = time.strftime('%Y-%m-%d-%H:%M:%S',
                               time.localtime(time.time()))
    return utils.render('security_certificate.html',
                        {'local_time': local_time,
                         'phone': user[0].phone})


@require_auth
def headimg(req):
    pass


class NameCertification(generic.FormView):

    form_class = forms.NameCertificationForm
    template_name = 'portal/name_certificate.html'

    def form_valid(self, form):
        user = utils.get_user_obj(self.request)
        data = form.cleaned_data
        if user:
            user.real_name = data['real_name']
            user.real_id = data['real_id']
            user.save()
            return info(self.request)
        else:
        #LOG.debug("%s name certificate failed." % user)
            return utils.render('name_certificate.html',
                                {'errors': 'failed',
                                 'form': form})

namecertificate = NameCertification.as_view()


class PasswordModify(generic.FormView):

    form_class = forms.PasswordModifyForm
    template_name = 'portal/password_modify.html'

    def form_valid(self, form):
        user = utils.get_user_obj(self.request)
        data = form.cleaned_data
        if user and user.password == data['password'] and \
           data['new_password'] == data['confirm_new_password']:
            user.password = data['new_password']
            user.save()
            return info(self.request)
        else:
        #LOG.debug("%s password modify failed." % user)
            return utils.render('password_modify.html',
                                {'errors': 'password is wrong',
                                 'form': form})

passwordmodify = PasswordModify.as_view()


class PhoneModify(generic.FormView):
    
    form_class = forms.PhoneModifyForm
    template_name = 'portal/phone_modify.html'
    def form_valid(self, form):
        user = utils.get_user_obj(self.request)
        data = form.cleaned_data
        if user and data['verification_code'] == str(user.verifycode):
            user.phone = data['newphone']
            user.is_active = False
            user.save()
            return info(self.request)
        else:
            user.is_active = False
            user.save()
            return utils.render('phone_modify.html',
                               {'errors': 'verifycode is wrong!',
                                'form': form})

phonemodify = require_auth(PhoneModify.as_view()) 


class SendVerifyCode(generic.FormView):
    
    form_class = forms.SendVerifyCodeForm
    template_name = 'portal/send_verifycode.html'

    def form_valid(self, form):
        user = utils.get_user_obj(self.request)
        data = form.cleaned_data
        if user and data['newphone']:
            if user.is_active == False:
                user.verifycode = random.randrange(0, 999999)
                user.is_active = True               
                user.save()
                print user.verifycode
                content = 'verifycode:' + str(user.verifycode)
                utils.send_msg(data['phone'], content)
                return phonemodify(self.request)
            else:
                return phonemodify(self.request)
        else:           
            return utils.render('phone_modify.html',
                                {'errors': 'failed',
                                 'form': form})


sendverifycode = require_auth(SendVerifyCode.as_view())


class MailboxModify(generic.FormView):

    form_class = forms.MailboxBindingForm
    template_name = 'portal/mailbox_binding.html'

    def form_valid(self, form):
        user = utils.get_user_obj(self.request)
        data = form.cleaned_data
        if user and data['email']:
            para = user.username
            content = 'click here to active ' + \
                    '<a href="http://localhost:8000/z/account/activate_mailbox/?username=' + \
                    para + '">' + \
                    'http://www.active.com</a>'
            utils.send_mail(data['email'], content)    
            for i in range(120):
                time.sleep(1)
                user = utils.get_user_obj(self.request)
                if user.is_active == True: 
                    user.email = data['email']
                    user.is_active = False
                    user.save()
                    break
            return info(self.request)
        else:
        #LOG.debug("%s mailbox modify failed." % user)
            return utils.render('mailbox_modify.html',
                                {'errors': 'failed',
                                 'form': form})


mailboxbinding = MailboxModify.as_view()


class SecurityProblem(generic.FormView):

    form_class = forms.SecurityProblemForm
    template_name = 'portal/security_problem.html'

    def form_valid(self, form):
        user = utils.get_user_obj(self.request)
        data = form.cleaned_data
        if user and data['problem_one'] and \
           data['problem_two'] and data['problem_three']:
            user.problem_one = data['problem_one']
            user.problem_two = data['problem_two']
            user.problem_three = data['problem_three']
            user.save()
            return safe(self.request)
        else:
        #LOG.debug("%s failed." % user)
            return utils.render('security_problem.html',
                                {'errors': 'failed',
                                 'form': form})


security_problem = SecurityProblem.as_view()


@require_auth
def messages(request):
    user = utils.get_user_obj(request)
    message = user.message_set.all()
    return utils.render('account/account_messages.html',
                        {'message': message})


@require_auth
def payments(request):
    pass

@require_auth
def activatemailbox(request):
    user = utils.get_user_obj(request)
    user.is_active = True
    user.save()
    print 'activate have been worked'
    return utils.render('activate_mailbox.html', {})
