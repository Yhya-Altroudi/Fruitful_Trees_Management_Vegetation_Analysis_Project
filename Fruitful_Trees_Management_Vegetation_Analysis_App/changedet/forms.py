from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date


# this class represent one period (start_date, end_date) form
class OnePeriodForm(forms.Form):
    '''
    this class represent one period (start_date, end_date) form
    '''

    start_date = forms.DateField(label='Start Date',
                                 required=True,
                                 initial="2022-05-01",
                                 widget=forms.DateInput(
                                     attrs={'type': 'date'}))

    end_date = forms.DateField(label='End Date',
                               required=True,
                               initial="2022-08-30",
                               widget=forms.DateInput(attrs={'type': 'date'}))

    # clean funcion used for validation
    def clean(self):

        # get cleaned data from parent function
        cleaned_data = super(OnePeriodForm, self).clean()

        # get start date field and label
        start_date = cleaned_data.get('start_date')
        start_date_label = self.fields['start_date'].label

        # get end date field and label
        end_date = cleaned_data.get('end_date')
        end_date_label = self.fields['end_date'].label

        # call one period validator
        OnePeriodValidator(start_date, start_date_label,
                           end_date, end_date_label)

        # return cleaned data
        return cleaned_data


# this class represent two period (start_date, end_date) form
class TwoPeriodsForm(forms.Form):
    '''
     this class represent two period (start_date, end_date) form
    '''

    first_start_date = forms.DateField(label='First Start Date',
                                       required=True,
                                       initial="2013-08-01",
                                       widget=forms.DateInput(attrs={'type': 'date',
                                                                     'style': 'margin-left: 22px; margin-bottom: 6px;'}))  # add some styling

    first_end_date = forms.DateField(label='First End Date',
                                     required=True,
                                     initial="2013-09-30",
                                     widget=forms.DateInput(attrs={'type': 'date',
                                                                   'style': 'margin-left: 21px; '}))  # add some styling

    second_start_date = forms.DateField(label='Second Start Date',
                                        required=True,
                                        initial="2022-07-01",
                                        widget=forms.DateInput(attrs={'type': 'date'}))

    second_end_date = forms.DateField(label='Second End Date',
                                      required=True,
                                      initial="2022-07-30",
                                      widget=forms.DateInput(attrs={'type': 'date'}))

    # clean funcion used for validation
    def clean(self):

        # get cleaned data from parent function
        cleaned_data = super(TwoPeriodsForm, self).clean()

        # get first start date field and label
        first_start_date = cleaned_data.get('first_start_date')
        first_start_date_label = self.fields['first_start_date'].label

        # get first end date field and label
        first_end_date = cleaned_data.get('first_end_date')
        first_end_date_label = self.fields['first_end_date'].label

        # call one period validator
        OnePeriodValidator(first_start_date, first_start_date_label,
                           first_end_date, first_end_date_label)

        # get second start date field and label
        second_start_date = cleaned_data.get('second_start_date')
        second_start_date_label = self.fields['second_start_date'].label

        # get second end date field and label
        second_end_date = cleaned_data.get('second_end_date')
        second_end_date_label = self.fields['second_end_date'].label

        # call one period validator
        OnePeriodValidator(second_start_date, second_start_date_label,
                           second_end_date, second_end_date_label)

        # call two period validator
        TwoPeriodValidator(first_end_date, first_end_date_label,
                           second_start_date, second_start_date_label)

        # return cleaned data
        return cleaned_data


# these fuctions are for applying validatos

# one period level validator
def OnePeriodValidator(start_date, start_date_label, end_date, end_date_label):
    '''
    one period level validator
    '''

    # Validation laws in this validator
    # 1. start date mustn't be lower than the date of fisrt landsat7 satellite image
    if start_date < date(1999, 5, 28):
        raise forms.ValidationError(
            f"{start_date_label} should be greater than or equal 1999-05-28.")

    # 2. end date mustm't be higher than today's date
    elif end_date > date.today():
        raise forms.ValidationError(
            f"{end_date_label} should be {date.today()} or befor this date.")

    # 3. start date mustn't be higher or equal end date
    elif start_date >= end_date:
        raise forms.ValidationError(
            f"{start_date_label} mustn't be greater than or equal End Date.")

    # 4. the distance between start date and end date mustn't be lower than 15 days
    elif (end_date - start_date).days <= 15:
        raise forms.ValidationError(
            "The days between start and end date should be mor than 15 days.")

# two period level validator


def TwoPeriodValidator(first_end_date, first_end_date_label, second_start_date, second_start_date_label):
    '''
     one period level validator
    '''

    # Validation laws in this validator
    # 1. first end date musn't be higher than second start date
    if first_end_date > second_start_date:
        raise forms.ValidationError(
            f"{first_end_date_label} shouldn't be bigger than {second_start_date_label}")


# satellite first image date
# landsat8 2013-03-18
# landsat7 1999-05-28
