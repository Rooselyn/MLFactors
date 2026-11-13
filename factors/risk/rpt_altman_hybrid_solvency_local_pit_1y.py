"""Altman启发的全行业会计偿债分数本地版（Hybrid solvency proxy）。
RE=未分配利润+盈余公积，EBIT*=利润总额+利息费用；均为已披露同年年报。
非金融：1.2(CA−CL)/A+1.4RE/A+3.3EBIT*/A+0.6MV/L+0.999Revenue/A。
银行/非银金融：1.4RE/A+3.3NetIncome/A+0.6MV/L。
金融分支为本地自定义盈利/资本/估值组合，不宣称原Altman模型或破产概率。
来源: [Altman原论文PDF](https://mx.nthu.edu.tw/~jtyang/Teaching/Corporate_Governance/Papers/Altman%201968.pdf)；[原论文PDF镜像](https://www.calctopia.com/papers/Altman1968.pdf)
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

FIELDS = {
    'ca':('financial_balance_sheet','total_cur_assets'),
    'cl':('financial_balance_sheet','total_cur_liab'),
    'a':('financial_balance_sheet','total_assets'),
    'l':('financial_balance_sheet','total_liab'),
    'u':('financial_balance_sheet','undistr_porfit'),
    's':('financial_balance_sheet','surplus_rese'),
    'p':('financial_income','total_profit'),
    'i':('financial_income','fin_exp_int_exp'),
    'n':('financial_income','n_income'),
    'r':('financial_income','revenue'),
}
INPUTS={field:ParquetInput(f'MLFactors/data/zz500/{table}/*/*.parquet',field,
    date_column='ann_date',announcement_columns=('f_ann_date','ann_date'),filters=(('report_type','1'),))
    for table,field in FIELDS.values()}
INPUTS.update({field:ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet',field)
               for field in ['total_mv','industry_sw_1']})
SPEC={'name':'rpt_altman_hybrid_solvency_local_pit_1y','engine':'financial','annual':True,
      'leaves':{key:[table,field,'Y',0] for key,(table,field) in FIELDS.items()}}
INDUSTRIAL='1.2*(ca-cl)/a+1.4*(u+s)/a+3.3*(p+i)/a+.6*MC/l+.999*r/a'
FINANCIAL='1.4*(u+s)/a+3.3*n/a+.6*MC/l'
FINANCIAL_INDUSTRIES=['银行','非银金融','银行(申万)','非银金融(申万)',
                      '801780','801790','801780.SI','801790.SI']

@register_factor
@fixed_factor('rpt_altman_hybrid_solvency_local_pit_1y', {})
class Factor_rpt_altman_hybrid_solvency_local_pit_1y(PublicFactor):
    name='rpt_altman_hybrid_solvency_local_pit_1y'
    description='Altman启发的全行业会计偿债分数本地版（Hybrid solvency proxy）'
    INPUTS=INPUTS
    SPEC=SPEC
    warmup_days=100000

    def generate_signals(self,data,constituents=None):
        dates=pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
        symbols=data.index.get_level_values('symbol').unique().sort_values()
        reports=_formula_calculations.read_reports(self.INPUTS,end=dates.max(),symbols=list(symbols))
        env,self.available_ann_dates=_formula_calculations.leaf_panels(self.SPEC,reports,dates,symbols,return_available=True)
        env['MC']=data.total_mv.unstack('symbol').reindex(index=dates,columns=symbols).where(lambda x:x>0)*10000
        industry=data.industry_sw_1.unstack('symbol').reindex(index=dates,columns=symbols).astype('string')
        ordinary=_formula_calculations.evaluate_expression(INDUSTRIAL,env)
        financial=_formula_calculations.evaluate_expression(FINANCIAL,env)
        value=ordinary.where(~industry.isin(FINANCIAL_INDUSTRIES),financial)
        value=value.where(industry.notna()&industry.apply(lambda x:x.str.strip().ne('')))
        return value.replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
