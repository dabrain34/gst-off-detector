from threading import Thread
import openfoodfacts
import time

class CheckProduct(Thread):
    def __init__(self, barcode, _finish_cb):
      ''' Constructor. '''
      Thread.__init__(self)
      self.barcode = barcode
      self.product = None
      self.running = False
      self._finish_cb = _finish_cb

    def get_results (self):
      return self.barcode

    def run(self):
      product = openfoodfacts.products.get_product(self.barcode)
      self._finish_cb(product)


class CheckOFF():
  def __init__(self):
    self.barcode = None
    self.product = None
    self.checking = True;
    self.myCheckProd = None

  def default_finish_cb (self, result):
    import pdb; pdb.set_trace()
    print ("%s" % result);

  def check_open_food_facts (self, barcode):
    if self.barcode == barcode:
      #print("no new thread")
      return;
    self.barcode = barcode
    self.myCheckProd = CheckProduct(barcode, self.default_finish_cb)
    self.myCheckProd.start()

  def check_open_food_facts_with_cb (self, barcode,_finish_cb):
    if self.barcode == barcode:
      #print("no new thread")
      return;
    self.barcode = barcode
    self.myCheckProd = CheckProduct(barcode, _finish_cb)
    self.myCheckProd.start()

  def wait_to_complete(self):
    if self.myCheckProd:
      self.myCheckProd.join()

# Run following code when the program starts
if __name__ == '__main__':
   # Declare objects of MyThread class
   myOff = CheckOFF()
   myOff.check_open_food_facts("8410700005359")
   # Wait for the threads to finish...
   myOff.wait_to_complete()

   print('Main Terminating...')
