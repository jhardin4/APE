import Core
import Procedures

import Project_Procedures.MJfunctions as SpanML  # functions specifically for segmenting spanning segments + making class predictions

# this will segment images of se 1700 silicone with blue pigment dye


class ImPredict(Core.Procedure):
    def Prepare(self):
        self.name = 'ImPredict'
        self.requirements['initial_file'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'path of initial image file',
        }
        self.requirements['final_file'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'path of final image file',
        }
        self.apparatus.createAppEntry(
            [
                'information',
                'ProcedureData',
                'SpanningSample',
                'cur_parameters',
                'Class',
            ]
        )

        self.model = SpanML.loadModel('gnbGap4')
        # self.apparatus.createAppEntry(['information','ProcedureData','SpanningSample','cur_parameters','clfModel'])
        # self.apparatus.setValue(['information','ProcedureData','SpanningSample','cur_parameters','clfModel'], model)
        # print('ImPredict Prepare finished')

    def Plan(self):
        ifilename = self.requirements['initial_file']['value']
        ffilename = self.requirements['final_file']['value']
        samplename = self.apparatus.getValue(
            [
                'information',
                'ProcedureData',
                'SpanningSample',
                'cur_parameters',
                'samplename',
            ]
        )

        if self.apparatus.simulation:
            classstr = input('type input number')
            class_pred = classstr
        else:

            gapPadded_thresh = SpanML.SpanningIP(
                ffilename, ifilename, samplename, path=True, save=False
            )
            # binary_img, gapPadded_thresh = SpanML.SpanningIP(ffilename, ifilename, samplename, path = True, save = False)
            # model = SpanML.loadModel('testsave_svmcmodel')
            class_pred_raw = str(
                SpanML.VBOW_class(self.model, gapPadded_thresh)
            )  # need a path
            class_pred = class_pred_raw.replace('[', '').replace(']', '')

        self.apparatus.setValue(
            [
                'information',
                'ProcedureData',
                'SpanningSample',
                'cur_parameters',
                'Class',
            ],
            class_pred,
        )
