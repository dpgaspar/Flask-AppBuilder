from flask_babel import lazy_gettext as _  
from wtforms.validators import ValidationError, Optional

# DEMO of business level field validation logic
# See: https://wtforms.readthedocs.io/en/stable/validators.html
class MySalaryValidator(object): #extends object
    """
	doc here
    """
    def __init__(self, min= -1000, max= None ):
        self.min = min
        self.max = max
        self.message = _('Out of allowed range')

    def __call__(self, form, field):		
        data = field.data
        data2 = form['full_name'].data 	# <<-- if other fields data are needed to make a decision		
        print("=== MySalaryValidator working on: \n", data, "\n", data2)   #debug
        erro = False
        if not data:
            erro = True
        else:
            #val = float(data)  # not needed, it seems that data is a decimal.Decimal or Float at this point
            val = data
            if(val < self.min):
                erro = True
            if self.max and (val > self.max):
                erro = True
        if erro:
            raise ValidationError(self.message)

