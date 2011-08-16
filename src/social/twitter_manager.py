'''
credentials

usr= nmgrl
pwd=Argon4039

'''
import twitter

class TwitterManager(object):
    def __init__(self,*args,**kw):
        self.tapi=twitter.Api(consumer_key='8mdnnhVEhOlT7Xu8Mg',
                                   consumer_secret='IzMqOxjSemTXyjZ8VCelFpUXdrhD77E74SV6mdrl7E',
                                   access_token_key='27101038-lzzwYplffclywtSAWnfbuB3ovrnPgmqkWMFqO2jvf',
                                   access_token_secret='BOea1U7aUoQXJEQ1CldvrK5RkjLImfXGls6PbuQw'
                                   )
    def verify(self):
        print self.tapi.VerifyCredentials()
        
    def post(self, msg):
        self.tapi.PostUpdate(msg)
    
if __name__ == '__main__':
    m=TwitterManager()
    m.verify()
    m.post('test mesg')