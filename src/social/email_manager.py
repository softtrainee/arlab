#=============enthought library imports=======================
from traits.api import HasTraits, Str, Enum, Bool, List, Password, Int
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.manager import Manager
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
class User(HasTraits):
    name=Str
    email=Str
    email_enabled=Bool
    email_level=Enum(0,1,2)
    telephone=Str
    
    
    def edit_view(self):
        return View('name',
                    'email',
                    'email_level',
                    'telephone'
                    
                    )
class EmailManager(Manager):
    users=List(User)
    
    outgoing_server=Str
    port=Int(587)
    sender=Str('Pychron')
    server_username=Str
    server_password=Password
    
    _server=None
    def traits_view(self):
        v=View(Item('users',show_label=False,
                    editor=TableEditor(columns=[ObjectColumn(name='name'),
                                                
                                                CheckboxColumn(name='email_enabled')
                                                ],
                                       orientation='vertical',
                                       edit_view='edit_view',
                                       show_toolbar=True,
                                       row_factory=self.row_factory
                                       )
                    ),
               width=500,
               height=400,
               resizable=True
               )
        return v
    
    def row_factory(self):
        u=User(name='moo')
        self.users.append(u)
    
    def get_emails(self):
        return [u.email for u in self.users]
    
    def _message_factory(self,text):
        msg=MIMEMultipart()
        msg['From']=self.sender#'nmgrl@gmail.com'
        msg['To']=', '.join(self.get_emails())
        msg['Subject']='!Pychron Alert!'
        
        msg.attach(MIMEText(text))
        return msg
    
    def connect(self):
        if self._server is None:
            server=smtplib.SMTP(self.outgoing_server,self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            server.login(self.server_username, self.server_password)
            self._server=server
        return self._server
    
    def broadcast(self, text):

        recipients=self.get_emails()
        if recipients:
            msg=self._message_factory(text)
            
            server=self.connect()
            server.sendmail(self.sender, recipients, msg.as_string())        
            server.close()
        
if __name__ == '__main__':
    em=EmailManager()
    em.users=[
              User(name='foo', 
                   email='jirhiker@gmail.com'
                   ),
              User(name='moo',
                   email='nmgrlab@gmail.com'
                   )
              ]
    em.broadcast()
    #em.configure_traits()
#============= EOF =====================================
