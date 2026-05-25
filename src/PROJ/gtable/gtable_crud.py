import pathlib
from pprint import pprint, pformat
import logging

import gspread
from gspread import Spreadsheet, Worksheet
from gspread.exceptions import APIError
from gspread.utils import ValueInputOption
from rich.logging import RichHandler

from src.PROJ.api.schemas_jobs import VacancyData
from src.PROJ.core.config import GOOGLE_CREDENTIALS_JSON
from src.PROJ.core.utils import time_counter

ROOT_DIR = pathlib.Path(__file__).parent
TABLE_ID_KEY = "1r24jFrWTHo5QMoG2mc32B6t7yQ32QsJcIyXuhOl1_2A"
DEFAULT_WORKSHEET_INDEX = 1  # from zero
DEFAULT_WORKSHEET_NAME = 'PROD'
FROZEN_HEADER_ROWS = 3

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(markup=True)])  # RichHandler() # level="NOTSET"
log = logging.getLogger("rich")


class GTable:
    def __init__(self, spreadsheet_id: str = None, worksheet_index: int = None, from_file=False):
        CREDENTIALS_FILE = "credentials.json"
        CREDENTIALS_PATH = ROOT_DIR.joinpath(CREDENTIALS_FILE)

        if from_file and CREDENTIALS_PATH.exists():
            self.gc = gspread.service_account(filename=CREDENTIALS_PATH)
        else:
            try:
                self.gc = gspread.service_account_from_dict(info=GOOGLE_CREDENTIALS_JSON)
            except Exception as e:
                log.error(e)
                raise ValueError('Check credentials.json env string') from e

        self.sh: Spreadsheet = self.gc.open_by_key(spreadsheet_id)
        self.worksheet1: Worksheet = self.sh.sheet1

    def _get_metadata(self):
        """returns numberFormat types"""
        cell_label = "A1:J1"
        return self.sh.fetch_sheet_metadata({
            'includeGridData': False,
            'ranges': [f"{DEFAULT_WORKSHEET_NAME}!{cell_label}"],
            'fields': 'sheets.data.rowData.values.effectiveFormat.numberFormat'
        })

    def get_info(self) -> dict:
        worksheets = self.sh.worksheets()
        worksheet_info = dict(sheet_title=self.sh.title,
                              count_worksheets=len(worksheets),
                              names=[(worksheet.title, "id " + str(worksheet.index), worksheet.row_count)
                                     for worksheet in worksheets],
                              worksheet1_prop=self.worksheet1._properties,
                              wsh2_prod_prop=self.sh.get_worksheet(1)._properties,
                              url=worksheets[0].url,
                              )

        metadata = self._get_metadata()
        logging.warning(f"{metadata=}")
        return worksheet_info

    def get_all_from2row(self):
        # ValueRenderOption: FORMATTED_VALUE, UNFORMATTED_VALUE, FORMULA
        return self.worksheet1.get_all_records(head=2)

    def print_all_records(self):
        worksheet = self.sh.sheet1
        list_of_dicts = worksheet.get_all_records()
        log.info(f'{list_of_dicts=}')

    def _delete_range(self, worksheet: Worksheet, start_index, end_index, table: Spreadsheet = None):
        """G LIMIT: SAVE at least 1 EMPTY ROW BEFORE DELETE"""

        if not table:
            table = self.sh

        # worksheet.batch_clear() # table.batch_clear(range=f'{start_cell}:{end_cell}')

        if start_index == end_index:
            worksheet.delete_rows(start_index)
        else:
            worksheet.delete_rows(start_index, end_index)

        log.warning(f"[red] sh: {worksheet.title}: Deleted data range indexes {start_index}:{end_index}[/]",
                    extra={"markup": True})

    def add_from_dataframe(self, dataframe):
        self.worksheet1.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

    def append(self, data):
        self.worksheet1.append_rows(values=[list(d.values()) for d in data],
                                    value_input_option=ValueInputOption.user_entered)

    @time_counter
    def add_to_sheet_vacancydata(self, data, sh_target_idx=DEFAULT_WORKSHEET_INDEX):
        if not data:
            log.warning('DEV: Write test data')
            raise NotImplementedError

        # check first item
        if isinstance(data[0], VacancyData):
            data = [data_item.model_dump() for data_item in data]
            # data = [data_item.model_dump(mode='json', include=include_values_set) for data_item in data]
        else:
            raise ValueError('data must be list of VacancyData')

        # show
        data_example = data[0].copy()
        data_example['text_'] = data_example['text_'][:20]
        log.warning(f"{data_example=}")

        # Delete prev + insert new
        sh_target = self.sh.get_worksheet(sh_target_idx)
        if not sh_target.title == DEFAULT_WORKSHEET_NAME:
            raise ValueError(f'Only {DEFAULT_WORKSHEET_NAME} sheet can be updated. Current: {sh_target.title}')

        try:
            sh_target.delete_rows(2, sh_target.row_count)
            log.warning(f'Done delete rows 2-{sh_target.row_count} in {sh_target.title}')
        except APIError as e:
            logging.error(e, exc_info=True)
        except Exception as e:
            logging.error(e)

        TARGET_ROW = 1

        log_data = (f'[cyan] TABLE INFO:\n'
                    f'{pformat(self.get_info(), sort_dicts=False)}\n'
                    f'{sh_target.column_count=}, {sh_target.row_count=}\n'
                    f'{sh_target.frozen_row_count=}, {sh_target.frozen_col_count=}\n'
                    f'>>> INSERT target: {sh_target.title}; {TARGET_ROW=}...\n'
                    f'[/]')
        log.warning(log_data, extra={"markup": True})

        prep_values = [list(d.values()) + ['=now()'] for d in data]  # header_list = list(data[0].keys())
        rows_count = len(prep_values)
        try:
            sh_target.insert_rows(values=prep_values, value_input_option=ValueInputOption.user_entered, row=TARGET_ROW)
        except Exception as e:
            raise

        log.warning(f'✅ Done insert to {sh_target.title} (+{rows_count})')

@time_counter
def g_table_main(data):
    gt = GTable(spreadsheet_id=TABLE_ID_KEY)
    gt.add_to_sheet_vacancydata(data)
    log.info(f'Gtable process done!')


if __name__ == '__main__':
    gt = GTable(spreadsheet_id=TABLE_ID_KEY)
    pprint(gt.get_info(), sort_dicts=False)
    # gt.add_to_sheet()
