# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Contributors: Brian Resnick
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from neon_utils.skills.neon_skill import NeonSkill
from adapt.intent import IntentBuilder
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from .ql800Printer import Printer
from datetime import datetime


class PrintLabel(NeonSkill):  
    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(network_before_load=False,
                                   internet_before_load=False,
                                   gui_before_load=False,
                                   requires_internet=False,
                                   requires_network=False,
                                   requires_gui=False,
                                   no_internet_fallback=True,
                                   no_network_fallback=True,
                                   no_gui_fallback=True)
                                   
    @intent_handler(IntentBuilder('PrintLabelIntent').require('PrintKeyword').require('LabelKeyword'))
    def handle_print_label_intent(self, message):
        date = datetime.today().strftime('%m/%d/%Y')
        self.log.info(date)

        # testing extract_number
        utt = message.data.get('utterance')
        self.log.info("!BR - " + utt)  # Diagnostic
        offset_label = utt.find("label")
        possible_qty_text = utt[:offset_label]
        self.log.info("Possible qty text: " + possible_qty_text)
        qty = int(extract_number(possible_qty_text))
        if qty == 0:
          # Check for 'to' instead of 'two' and 'for' instead of 'four'
          if possible_qty_text.find("to") >= 0:
            qty = 2
          elif possible_qty_text.find("for") >= 0:
            qty = 4
          else:
            qty = 1
          pass
        self.log.info(qty)
        # Check for description which begins with "for" after "label(s)"
        post_label_text = utt[offset_label + 5:]
        offsetFor = post_label_text.find("for")
        if (offsetFor > -1):
           description = post_label_text[offsetFor+4:]
           description = description.upper()
           self.log.info(description)  # Diagnostic
           self.printer.print_label_two_lines(date, description, qty)
        else:
           self.printer.print_label_one_line(date, qty)
           pass

    def stop(self):
        pass           


# def create_skill():
#    return PrintLabel()