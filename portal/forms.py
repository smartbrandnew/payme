# -*- coding: utf-8 -*-
"""
All the forms located here.
"""

from django import forms
from django.core.exceptions import ValidationError

from portal import models


##### validators ########
def valid_fixed_length(value):
    if len(value) == 18 or len(value) == 15:
        return True
    else:
        raise ValidationError(u'should length in 15 or 18')


#### forms #######
class SignUpForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    real_name = forms.CharField()
    real_id = forms.CharField(validators=[valid_fixed_length])
    location_province = forms.CharField()
    location_city = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()


class MerchSignUpForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    real_name = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()



class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class VipForm(forms.Form):
    text = forms.CharField()


class ChargeRentForm(forms.ModelForm):
    class Meta:
        model = models.LandlordRentProfile
        exclude = ('landlord',)


class ChargeRenterForm(forms.ModelForm):
    class Meta:
        model = models.LandlordRenterInfo
        exclude = ('rent', 'service_expense', 'total_expense',
                   'state', 'uuid')


class PayRentCreateForm(forms.ModelForm):
    class Meta:
        model = models.RenterRentProfile
        exclude = ('renter', 'uuid')


class PayRentOptionCreateForm(forms.ModelForm):
    class Meta:
        model = models.RenterOption
        exclude = ('rent_profile', 'state', 'confirmed', 'service_expense')


class AddHouseForm(forms.ModelForm):
    class Meta:
        model = models.House
        exclude = ('owner',)


class ChangePasswordForm(forms.Form):
    oldpassword = forms.CharField()
    newpassword = forms.CharField()
    newpassagain = forms.CharField()


class AddRentalAccountForm(forms.ModelForm):
     class Meta:
        model = models.RentalAccount
        exclude = ('owner',)


class AddAccountMoneyForm(forms.ModelForm):
    class Meta:
        model = models.AccountMoney
        exclude = ('owner','created_at')


class MerchantConfirmForm(forms.ModelForm):
    class Meta:
        model = models.MerchantConfirm
        exclude = ('owner','state')


class PasswordModifyForm(forms.Form):
    password = forms.CharField()
    new_password = forms.CharField()
    confirm_new_password = forms.CharField()


class PhoneModifyForm(forms.Form):
    newphone = forms.CharField()
    verification_code = forms.CharField()

class SendVerifyCodeForm(forms.Form):
    newphone = forms.CharField()


class MailboxBindingForm(forms.Form):
    email = forms.EmailField()

class NameCertificationForm(forms.Form):
    real_name = forms.CharField()
    real_id = forms.CharField(validators=[valid_fixed_length])

class SecurityProblemForm(forms.Form):
    problem_one = forms.CharField()
    problem_two = forms.CharField()
    problem_three = forms.CharField()


class HeadImgForm(forms.Form):
    front_img = forms.ImageField()
