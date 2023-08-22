#!/usr/bin/env python3
from os.path import basename, dirname, join

from processing import createAlgorithmDialog
from qgis.core import (
    QgsProcessing,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterVectorLayer,
)
from qgis.PyQt.QtCore import QPoint, QRect, QSize
from qgis.utils import Qgis, plugins

plugin_name = basename(dirname(dirname(__file__)))
provider = plugins[plugin_name].provider


PATH = '/processing'

TEMPLATE = '''---
hide:
  - navigation
---

# Processing
'''

TEMPLATE_GROUP = '''
## {group}

'''

TEMPLATE_ALGORITHM = '''
### {title}

{help_string}

![algo_id]({img})

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
{parameters}

#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
{outputs}

***

'''

TEMPLATE_PARAMETERS = '{id}|{description}|{type}|{info}|{required}|{advanced}|{option}|\n'

TEMPLATE_OUTPUT = '{id}|{description}|{type}|{info}|\n'


def format_type(class_name):
    class_name = class_name.replace('QgsProcessingParameter', '')
    class_name = class_name.replace('QgsProcessingOutput', '')
    return class_name


def generate_processing_doc():  # NOQA C901
    global TEMPLATE

    markdown_all = TEMPLATE
    algorithms_markdown = {}

    for alg in provider.algorithms():

        output_screen = join(PATH, '{}.jpg'.format(alg.id().replace(':', '-')))
        alg_dialog = createAlgorithmDialog(alg.id())
        alg_dialog.resize(1100, 800)
        screen = alg_dialog.grab(QRect(QPoint(0, 0), QSize(-1, -1)))
        screen.save(output_screen)

        param_markdown = ''
        for param in alg.parameterDefinitions():
            if hasattr(param, 'tooltip_3liz'):
                info = param.tooltip_3liz
            else:
                info = ''

            if Qgis.QGIS_VERSION_INT >= 31500 and not info:
                info = param.help()

            dict_type = {
                -1: 'VectorAnyGeometry',
                -2: 'MapLayer',
                0: 'Point',
                1: 'Line',
                2: 'Polygon',
                3: 'Raster',
                4: 'File',
                5: 'Vector',
                6: 'Mesh'
            }

            option = ''
            if param.defaultValue():
                option += 'Default: ' + str(param.defaultValue()) + ' <br> '

            if isinstance(param, QgsProcessingParameterNumber):
                if param.dataType() == QgsProcessingParameterNumber.Double:
                    name_type = 'Double'
                else:
                    name_type = 'Integer'
                option += 'Type: ' + name_type + '<br> '
                if param.minimum():
                    option += 'Min: ' + str(param.minimum()) + ', '
                if param.maximum():
                    option += 'Max: ' + str(param.maximum()) + ' <br>'
            elif isinstance(param, QgsProcessingParameterVectorLayer):
                option += 'Type: '
                if Qgis.QGIS_VERSION_INT < 30600:
                    name_types = [dict_type[item] for item in param.dataTypes()]
                    option += ', '.join(name_types) + ' <br>'
                else:
                    name_types = [QgsProcessing.sourceTypeToString(item) for item in param.dataTypes()]
                    option += ', '.join(name_types) + ' <br>'

            elif isinstance(param, QgsProcessingParameterFeatureSink):
                option += 'Type: '
                if Qgis.QGIS_VERSION_INT < 30600:
                    option += dict_type[param.dataType()] + ' <br>'
                else:
                    option += QgsProcessing.sourceTypeToString(param.dataType()) + ' <br>'

            elif isinstance(param, QgsProcessingParameterEnum):
                list_value = param.options()
                option += 'Values: '
                option += ', '.join(list_value) + ' <br>'

            param_markdown += TEMPLATE_PARAMETERS.format(
                id=param.name(),
                type=format_type(param.__class__.__name__),
                description=param.description(),
                info=info,
                required='' if param.flags() & QgsProcessingParameterDefinition.FlagOptional else '✓',
                advanced='✓' if param.flags() & QgsProcessingParameterDefinition.FlagAdvanced else '',
                option=option
            )

        output_markdown = ''
        for output in alg.outputDefinitions():
            if hasattr(output, 'tooltip_3liz'):
                info = output.tooltip_3liz
            else:
                info = ''
            output_markdown += TEMPLATE_OUTPUT.format(
                id=output.name(),
                type=format_type(output.__class__.__name__),
                description=output.description(),
                info=info,
            )

        markdown = TEMPLATE_ALGORITHM.format(
            title=alg.displayName(),
            help_string=alg.shortHelpString() if alg.shortHelpString() else '',
            parameters=param_markdown if param_markdown else 'No parameter',
            outputs=output_markdown if output_markdown else 'No output',
            img=f'./{basename(output_screen)}',
            algo_id=alg.id(),
        )

        if alg.group() not in algorithms_markdown.keys():
            algorithms_markdown[alg.group()] = []

        algorithms_markdown[alg.group()].append(markdown)

    for group in algorithms_markdown.keys():
        markdown_all += TEMPLATE_GROUP.format(group=group)
        for alg in algorithms_markdown[group]:
            markdown_all += alg

    output_file = join(PATH, 'README.md')
    # output_file = join('/home/pdrillin/dev/', 'README.md')
    text_file = open(output_file, "w+", encoding='utf8')
    text_file.write(markdown_all)
    text_file.close()


generate_processing_doc()
