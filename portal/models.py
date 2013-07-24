# -*- coding: utf-8 -*-
"""
Database models are defined here.
"""
import datetime
from uuid import uuid4

from django.forms.models import model_to_dict
from django.db.models import Model
from django.db.models import IntegerField, CharField, DateTimeField, FloatField
from django.db.models import DateField, EmailField, BooleanField, ImageField
from django.db.models import ForeignKey, OneToOneField
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


STATES = dict((
    ('0', _('NoConfirm')),
    ('1', _('NoPay')),
    ('2', _('Verify')),
    ('3', _('VerifyPassed')),
    ('4', _('VerifyFailed')),
    ('5', _('Canceled'))
))

RENT_TYPES = [('1', _('house')), ('2', _('shop'))]

ROOM_COUNTS = [('1', _('1 rooms')), ('2', _('2 rooms')),
               ('3', _('3 rooms')), ('4', _('>=4 rooms'))]

ARRIVE_TYPES = [('1', _('next day')), ('2', _('two hours'))]

DECKS = [('1', _('lowest')),
         ('2', _('basic')),
         ('3', _('normal')),
         ('4', _('higest')),
         ]


class BaseModel(object):
    def as_dict(self):
        return model_to_dict(self)

    def update_from_dict(self, new_fields):
        for key, value in new_fields.items():
            setattr(self, key, value)


class User(Model, BaseModel):
    
    username = CharField(_('username'), max_length=255,
                         db_index=True, unique=True)
    password = CharField(_('password'), max_length=255)
    phone = CharField(_('phone'), max_length=20, db_index=True)
    real_name = CharField(_('real name'), max_length=255)
    real_id = CharField(_('real id'), max_length=40)
    email = EmailField(_('email'))
    signup_at = DateTimeField(_('signup at'), auto_now_add=True)
    avater = CharField(_('avater'), max_length=255)
    location_province = CharField(_('loc province'), max_length=255)
    location_city = CharField(_('loc city'), max_length=255)
    front_image = ImageField(upload_to='upload')
    back_image = ImageField(upload_to='upload')
    problem_one = CharField(max_length=255)
    problem_two = CharField(max_length=255)
    problem_three = CharField(max_length=255)
    verifycode = CharField(max_length=255)
    is_vip = BooleanField(_('is vip'))
    is_active = BooleanField(default=False)

    created_at = DateTimeField(_('created at'), auto_now_add=True)


    def __unicode__(self):
        return self.username


class UserAdmin(admin.ModelAdmin):
    list_display = ['username']


class Merchant(Model, BaseModel):
    username = CharField(max_length=255, db_index=True, unique=True)
    password = CharField(max_length=255)
    real_name = CharField(max_length=255)
    phone = CharField(max_length=20, db_index=True)
    email = EmailField()




class MerchantAdmin(admin.ModelAdmin):
    list_display = ['username']


class Vip(Model, BaseModel):
    text = CharField(max_length=255)


class VipAdmin(admin.ModelAdmin):
    list_display = ['text']


##################################
class LandlordRentProfile(Model, BaseModel):
    """A user who is landlord can have many rent."""
    landlord = ForeignKey(User)

    rent_type = CharField(_('rent_type'), max_length=2, choices=RENT_TYPES)
    room_count = CharField(_('room count'), max_length=2, choices=ROOM_COUNTS)
    deck = CharField(_('deck'), max_length=2, choices=DECKS)
    acreage = IntegerField(_('acreage'))
    loc_province = CharField(_('loc province'), max_length=50)
    loc_city = CharField(_('loc city'), max_length=50)
    loc_area = CharField(_('loc are'), max_length=50)
    loc_cell = CharField(_('loc cell'), max_length=50)
    loc_addr = CharField(_('loc addr'), max_length=50)

    payee_name = CharField(_('payee name'), max_length=255)
    payee_id_card = CharField(_('payee id card'), max_length=20)
    payee_bank = CharField(_('payee bank'), max_length=255)
    payee_bank_card = CharField(_('payee bank card'), max_length=50)
    payee_bank_province = CharField(_('payee bank province'), max_length=50)
    payee_bank_city = CharField(_('payee bank city'), max_length=50)

    created_at = DateTimeField(_('created at'), auto_now_add=True)

    @property
    def pretty_name(self):
        """Return a beatifull name like: cellname|1 room| hight| 123m2"""
        return '|'.join([unicode(self.loc_cell), unicode(self.room_count),
                         unicode(self.deck), unicode(self.acreage)])

    @property
    def uncanceled_renters(self):
        return self.landlordrenterinfo_set.filter(state__lt=5)

    @property
    def renter_count(self):
        return self.uncanceled_renters().count()

    @property
    def renter_paied_count(self):
        return self.landlordrenterinfo_set.filter(state__gt=2).count()

    @property
    def total_expense(self):
        total = 0
        for renter in self.uncanceled_renters():
            total += renter.total_expense
        return total


class LandlordRenterInfo(Model, BaseModel):
    """A Landlord can have many renter. Each renter pay difference expense."""
    rent = ForeignKey(LandlordRentProfile)
    renter = ForeignKey(User)

    renter_name = CharField(_('renter name'), max_length=255)
    rent_expense = IntegerField(_('rent expense'), help_text=_('yuan/month'))
    rent_months = IntegerField(_('rent month'), help_text=_('months'))
    rent_begin_date = DateField(_('rent begin date'))
    rent_pay_model = CharField(_('rent pay model'),
        max_length=2, choices=[('1', 'one month'), ('2', 'three month'),
                               ('4', 'six month'), ('8', 'twenty month')])
    pay_months = IntegerField(_('pay months'))
    pay_begin_date = DateField(_('pay begin date'))
    deposit = IntegerField(_('deposit'), help_text=_('Yuan'))
    arrive_type = CharField(_('arrive type'), max_length=2,
                            choices=ARRIVE_TYPES)
    i_pay_it = BooleanField(_('i pay it'))

    service_expense = IntegerField(_('service expense'))
    total_expense = IntegerField(_('total expense'))
    created_at = DateTimeField(_('created at'), auto_now_add=True)

    state = CharField(_('state'), max_length=2, choices=STATES.items())
    uuid = CharField(_('uuid'), max_length=36, default=uuid4)

    def canceled(self):
        return self.state == '5'

    def cancel(self):
        self.state = '5'
        self.save()

    def state_str(self):
        return STATES[self.state]

    def pay_end_date(self):
        return self.pay_begin_date + datetime.timedelta(3 * 365 / 12)

    @property
    def pretty_name(self):
        return self.rent.pretty_name


class RenterRentProfile(Model, BaseModel):
    """A renter can rent many house."""
    renter = ForeignKey(User)

    rent_type = CharField(_('rent type'), max_length=2, choices=RENT_TYPES)
    room_count = CharField(_('room count'), max_length=2, choices=ROOM_COUNTS)
    deck = CharField(_('deck'), max_length=2, choices=DECKS)
    acreage = IntegerField(_('acreage'))

    rent_expense = IntegerField(_('rent expense'))
    rent_months = IntegerField(_('rent months'))
    rent_begin_date = DateField(_('rent begin date'))

    loc_province = CharField(_('loc province'), max_length=50)
    loc_city = CharField(_('loc city'), max_length=50)
    loc_area = CharField(_('loc area'), max_length=50)
    loc_cell = CharField(_('loc cell'), max_length=50)
    loc_addr = CharField(_('loc addr'), max_length=50)

    payee_type = CharField(_('payee type'), max_length=2,
                choices=[('1', 'person'), ('2', 'company')])
    payee_name = CharField(_('payee name'), max_length=255)
    payee_bank = CharField(_('payee bank'), max_length=255)
    payee_bank_card = CharField(_('payee bank card'), max_length=50)
    payee_bank_province = CharField(_('payee bank province'), max_length=50)
    payee_bank_city = CharField(_('payee bank city'), max_length=50)
    payee_phone = CharField(_('payee phone'), max_length=30)

    created_at = DateTimeField(_('created at'), auto_now_add=True)

    uuid = CharField(_('uuid'), max_length=36, default=uuid4)

    @property
    def state_str(self):
        return self.renteroption.state_str()

    @property
    def pretty_name(self):
        """Return a beatifull name like: cellname|1 room| hight| 123m2"""
        return u'|'.join([unicode(self.loc_cell), unicode(self.room_count),
                          unicode(self.deck), unicode(self.acreage)])

    @property
    def pay_months(self):
        return self.renteroption.pay_months

    @property
    def total_expense(self):
        return self.renteroption.total_expense

    @property
    def deposit(self):
        return self.renteroption.deposit

    @property
    def service_expense(self):
        return self.renteroption.service_expense

    @property
    def canceled(self):
        return self.renteroption.state == '5'

    def cancel(self):
        self.renteroption.state = '5'
        self.renteroption.save()


class RenterOption(Model, BaseModel):
    """A RenterRentProfile can only have one RenterOption"""
    rent_profile = OneToOneField(RenterRentProfile)

    pay_months = IntegerField(_('pay months'))
    pay_begin_date = DateField(_('pay begin date'))
    total_expense = IntegerField(_('total expense'))
    deposit = IntegerField(_('deposit'))
    comment = CharField(_('comment'), max_length=255)
    arrive_type = CharField(_('arrive type'), max_length=2,
                            choices=ARRIVE_TYPES)
    is_installment = BooleanField(_('is installment'))

    service_expense = IntegerField(_('service expense'))
    created_at = DateTimeField(_('created at'), auto_now_add=True)

    state = CharField(_('state'), max_length=2, choices=STATES.items())

    confirmed = BooleanField(_('confirmed'))

    def state_str(self):
        return STATES[self.state]

    @property
    def uuid(self):
        return self.rent_profile.uuid


class Message(Model, BaseModel):
    """User messages. A User will have many message to him"""
    owner = ForeignKey(User)
    content = CharField(_('content'), max_length=255)
    created_at = DateTimeField(_('created at'), auto_now_add=True)
    is_readed = BooleanField(_('is readed'))


class BankCard(Model, BaseModel):
    """A user will have many bank card."""
    owner = ForeignKey(User)
    bank_name = CharField(_('bank name'), max_length=50)
    card_user_name = CharField(_('card user name'), max_length=255)
    card_no = CharField(_('card number'), max_length=50)
    card_loc = CharField(_('card loc'), max_length=255)

    deleted = BooleanField()

    created_at = DateTimeField(_('created at'), auto_now_add=True)


####################################
class House(Model, BaseModel):
    """Merchant have many houses to renter"""
    owner = ForeignKey(Merchant)
    landlord = CharField(max_length=255)
    landphone = CharField(max_length=20)
    house_type = CharField(max_length=255)
    house_address = CharField(max_length=255)
    house_square = CharField(max_length=255)
    house_decoration = CharField(max_length=255)
    house_apartment = CharField(max_length=255)
    house_twords = CharField(max_length=20)
    house_floor = CharField(max_length=255)
    house_year = CharField(max_length=255)
    house_set = CharField(max_length=255)
    house_money = CharField(max_length=255)
    pay_type = CharField(max_length=255)
    house_deposit = CharField(max_length=255)
    rent_time = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)


class RentalAccount(Model, BaseModel):
    """Merchant have many rental accounts"""
    owner = ForeignKey(Merchant)
    account_type = CharField(max_length=255)
    account_name = CharField(max_length=255)
    rentalbank_name = CharField(max_length=255)
    rentalbank_num = CharField(max_length=255)
    account_address = CharField(max_length=255)


class AccountMoney(Model, BaseModel):
    """Merchant have the money to afford the order service charge"""
    owner = ForeignKey(Merchant)
    in_out_money = FloatField()
    operation_name = CharField(max_length=255)
    pay_type = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)


class MerhantMessage(Model, BaseModel):
    """Merchant messages. A Merchant will have many message to him"""
    owner = ForeignKey(Merchant)
    content = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    is_readed = BooleanField()


class MerchantConfirm(Model, BaseModel):
    """ Confirm Information need two pic,real name, real num"""
    owner = ForeignKey(Merchant)
    real_name = CharField(max_length=255)
    real_num = CharField(max_length=255)
    pic_face = ImageField(upload_to='savephoto/')
    pic_oppo = ImageField(upload_to='savephoto/')
    state = BooleanField()


class MechantConfirmAdmin(admin.ModelAdmin):
    list_display = ['owner']
