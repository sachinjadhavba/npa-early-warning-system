"""
npa_early_warning_system.py
============================
Rule-based Early Warning Indicator (EWI) System for SME Loan Portfolios
Author: Sachin Jadhav | 19 Yrs BFSI | Credit Risk & Portfolio Management
Website: https://finsight-one-4cao.vercel.app/
LinkedIn: https://www.linkedin.com/in/sachin-jadhav-consulting
Contact: jadhav.sachin6290@gmail.com

Based on real-world EWI frameworks used in Indian commercial banking.
All data is synthetically generated — no real customer data used.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
NAVY  = '#1F4E79'
BLUE  = '#2E75B6'
GREEN = '#27AE60'
AMBER = '#E6A817'
RED   = '#C0392B'
GRAY  = '#7F8C8D'

# ─── EWI TRIGGER DEFINITIONS ─────────────────────────────────────────────────
EWI_TRIGGERS = {
    'T1_emi_bounces': {
        'name': 'EMI Bounce Frequency',
        'description': 'Multiple EMI bounces in last 90 days',
        'weight': 2,
        'threshold': '2+ bounces = high risk, 1 bounce = watch',
        'real_world_note': 'Most reliable early signal — 78% predictive accuracy in practice'
    },
    'T2_cheque_dishonour': {
        'name': 'Cheque Dishonour',
        'description': 'Cheque dishonoured in last 60 days',
        'weight': 2,
        'threshold': 'Any dishonour = flag',
        'real_world_note': 'Combined with leverage, this is the strongest dual-signal'
    },
    'T3_turnover_drop': {
        'name': 'Monthly Turnover Decline',
        'description': 'Consistent drop in current account turnover',
        'weight': 2,
        'threshold': '>15% drop for 2 consecutive months = stress signal',
        'real_world_note': 'Cash flow stress shows here before EMI bounce'
    },
    'T4_high_leverage': {
        'name': 'High Leverage Ratio',
        'description': 'Total debt to net worth exceeds policy limits',
        'weight': 2,
        'threshold': '>3.5x = high risk, 2.5-3.5x = watch',
        'real_world_note': 'Cross-reference with industry benchmarks for context'
    },
    'T5_dpd_creep': {
        'name': 'DPD Creep',
        'description': 'Days Past Due increasing trend',
        'weight': 1,
        'threshold': '31-89 DPD = special mention territory',
        'real_world_note': 'Early classification prevents NPA build-up'
    },
    'T6_account_dormancy': {
        'name': 'Account Dormancy',
        'description': 'Low or no activity in operating account',
        'weight': 1,
        'threshold': '<3 transactions/month for CC/OD accounts',
        'real_world_note': 'Business activity proxy — dormant = stressed'
    },
    'T7_insurance_lapse': {
        'name': 'Insurance/Collateral Lapse',
        'description': 'Property or stock insurance not renewed',
        'weight': 1,
        'threshold': 'Any lapse = immediate flag',
        'real_world_note': 'Often overlooked — exposes bank to collateral risk'
    },
    'T8_industry_stress': {
        'name': 'Industry Stress Flag',
        'description': 'Borrower in a stressed industry sector',
        'weight': 1,
        'threshold': 'Sector NPA > 8% = watch all accounts in that sector',
        'real_world_note': 'Systematic risk — review all accounts in flagged sectors'
    }
}

EWI_RISK_LEVELS = {
    (0, 2): ('Normal', GREEN, 'Standard monitoring'),
    (3, 4): ('Watch', AMBER, 'Enhanced monitoring — monthly review'),
    (5, 6): ('Special Mention', '#E67E22', 'Immediate RM visit — restructure assessment'),
    (7, 99): ('Immediate Action', RED, 'Credit committee escalation — NPA prevention')
}

# ─── DATA GENERATOR ──────────────────────────────────────────────────────────
def generate_sample_portfolio(n=300, seed=42):
    np.random.seed(seed)
    segments = ['SME Manufacturing', 'Agri Processing', 'Retail Trade',
                'Service Sector', 'Construction', 'Healthcare']
    df = pd.DataFrame({
        'account_id':        [f'A{str(i).zfill(4)}' for i in range(1, n+1)],
        'borrower_name':     [f'Borrower {i}' for i in range(1, n+1)],
        'segment':           np.random.choice(segments, n, p=[0.35,0.20,0.20,0.12,0.08,0.05]),
        'sanction_amt_lac':  np.random.lognormal(5.5, 0.8, n).clip(25, 3000),
        'outstanding_lac':   None,
        'dpd':               np.random.choice([0,15,45,75,120], n, p=[0.62,0.18,0.11,0.06,0.03]),
        'emi_bounces_90d':   np.random.choice([0,1,2,3], n, p=[0.72,0.16,0.08,0.04]),
        'cheque_dishonour':  np.random.choice([0,1], n, p=[0.90,0.10]),
        'turnover_drop_pct': np.random.normal(2, 18, n),
        'leverage_ratio':    np.random.lognormal(0.8, 0.45, n),
        'monthly_txn_count': np.random.randint(0, 25, n),
        'insurance_lapsed':  np.random.choice([0,1], n, p=[0.88,0.12]),
        'industry_stress':   np.random.choice([0,1], n, p=[0.80,0.20]),
        'months_on_book':    np.random.randint(3, 96, n),
        'rm_name':           np.random.choice(['RM_A','RM_B','RM_C','RM_D','RM_E'], n),
    })
    df['outstanding_lac'] = df['sanction_amt_lac'] * np.random.uniform(0.35, 1.0, n)
    df['is_npa'] = df['dpd'] >= 90
    return df

# ─── CORE EWI SCORER ─────────────────────────────────────────────────────────
def score_ewi(df):
    """
    Score each account on 8 EWI triggers.
    Total score determines risk classification.
    """
    df = df.copy()
    df['ewi_score'] = 0
    df['triggers_fired'] = ''

    # T1: EMI Bounces
    df.loc[df['emi_bounces_90d'] >= 2, 'ewi_score'] += 2
    df.loc[df['emi_bounces_90d'] == 1, 'ewi_score'] += 1
    df.loc[df['emi_bounces_90d'] >= 2, 'triggers_fired'] += 'T1(HIGH) '
    df.loc[df['emi_bounces_90d'] == 1, 'triggers_fired'] += 'T1(WATCH) '

    # T2: Cheque Dishonour
    df.loc[df['cheque_dishonour'] == 1, 'ewi_score'] += 2
    df.loc[df['cheque_dishonour'] == 1, 'triggers_fired'] += 'T2 '

    # T3: Turnover Drop
    df.loc[df['turnover_drop_pct'] < -15, 'ewi_score'] += 2
    df.loc[df['turnover_drop_pct'].between(-15, -5), 'ewi_score'] += 1
    df.loc[df['turnover_drop_pct'] < -15, 'triggers_fired'] += 'T3(HIGH) '
    df.loc[df['turnover_drop_pct'].between(-15,-5), 'triggers_fired'] += 'T3(WATCH) '

    # T4: High Leverage
    df.loc[df['leverage_ratio'] > 3.5, 'ewi_score'] += 2
    df.loc[df['leverage_ratio'].between(2.5, 3.5), 'ewi_score'] += 1
    df.loc[df['leverage_ratio'] > 3.5, 'triggers_fired'] += 'T4(HIGH) '
    df.loc[df['leverage_ratio'].between(2.5,3.5), 'triggers_fired'] += 'T4(WATCH) '

    # T5: DPD Creep
    df.loc[df['dpd'].between(31, 89), 'ewi_score'] += 1
    df.loc[df['dpd'].between(31,89), 'triggers_fired'] += 'T5 '

    # T6: Account Dormancy
    df.loc[df['monthly_txn_count'] < 3, 'ewi_score'] += 1
    df.loc[df['monthly_txn_count'] < 3, 'triggers_fired'] += 'T6 '

    # T7: Insurance Lapse
    df.loc[df['insurance_lapsed'] == 1, 'ewi_score'] += 1
    df.loc[df['insurance_lapsed'] == 1, 'triggers_fired'] += 'T7 '

    # T8: Industry Stress
    df.loc[df['industry_stress'] == 1, 'ewi_score'] += 1
    df.loc[df['industry_stress'] == 1, 'triggers_fired'] += 'T8 '

    # Assign risk level
    def get_risk(score):
        for (low, high), (label, color, action) in EWI_RISK_LEVELS.items():
            if low <= score <= high:
                return label, color, action
        return 'Normal', GREEN, 'Standard monitoring'

    df[['risk_level','risk_color','recommended_action']] = df['ewi_score'].apply(
        lambda s: pd.Series(get_risk(s)))

    df['ewi_flagged'] = df['ewi_score'] >= 3
    df['triggers_fired'] = df['triggers_fired'].str.strip()

    return df

# ─── GENERATE RM ACTION LIST ─────────────────────────────────────────────────
def generate_rm_action_list(df):
    """
    Generate prioritised action list for Relationship Managers.
    This is the output that gets shared in weekly credit review meetings.
    """
    flagged = df[df['ewi_flagged']].copy()
    flagged = flagged.sort_values('ewi_score', ascending=False)

    print("\n" + "="*70)
    print("  EWI ACTION LIST — WEEKLY CREDIT REVIEW")
    print(f"  Generated: {datetime.today().strftime('%d %b %Y %H:%M')}")
    print(f"  Total Flagged: {len(flagged)} accounts")
    print("="*70)

    for _, row in flagged.head(10).iterrows():
        print(f"\n  {'⚠'*min(row['ewi_score'],3)} {row['account_id']} — {row['borrower_name']}")
        print(f"  Risk Level   : {row['risk_level']} (Score: {row['ewi_score']}/12)")
        print(f"  Segment      : {row['segment']}")
        print(f"  Outstanding  : ₹{row['outstanding_lac']:.1f} Lac")
        print(f"  DPD          : {row['dpd']} days")
        print(f"  Triggers     : {row['triggers_fired']}")
        print(f"  RM           : {row['rm_name']}")
        print(f"  Action       : {row['recommended_action']}")
        print("  " + "-"*65)

    return flagged

# ─── VISUALISATION ───────────────────────────────────────────────────────────
def plot_ewi_dashboard(df):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('EWI Dashboard — SME Portfolio Risk Monitor',
                 fontsize=16, fontweight='bold', color=NAVY, y=0.98)
    fig.patch.set_facecolor('white')

    # Panel 1: Risk Distribution
    ax1 = axes[0, 0]
    risk_counts = df['risk_level'].value_counts()
    risk_order = ['Normal', 'Watch', 'Special Mention', 'Immediate Action']
    risk_colors_map = {'Normal': GREEN, 'Watch': AMBER,
                       'Special Mention': '#E67E22', 'Immediate Action': RED}
    counts = [risk_counts.get(r, 0) for r in risk_order]
    colors = [risk_colors_map[r] for r in risk_order]
    bars = ax1.bar(risk_order, counts, color=colors, edgecolor='white', linewidth=0.5)
    for bar, count in zip(bars, counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(count), ha='center', fontsize=10, fontweight='bold', color=NAVY)
    ax1.set_title('Portfolio Risk Distribution', fontweight='bold', color=NAVY, pad=10)
    ax1.set_ylabel('Number of Accounts', color=GRAY)
    ax1.tick_params(axis='x', labelsize=8)
    ax1.spines[['top','right']].set_visible(False)

    # Panel 2: Trigger Frequency
    ax2 = axes[0, 1]
    trigger_counts = {}
    for t in ['T1','T2','T3','T4','T5','T6','T7','T8']:
        trigger_counts[t] = df['triggers_fired'].str.contains(t, na=False).sum()
    trigger_names = {'T1':'EMI Bounce','T2':'Cheque Dis.','T3':'Turnover',
                     'T4':'Leverage','T5':'DPD Creep','T6':'Dormancy',
                     'T7':'Insurance','T8':'Industry'}
    bars2 = ax2.barh([trigger_names[t] for t in trigger_counts.keys()],
                     list(trigger_counts.values()),
                     color=BLUE, edgecolor='white')
    ax2.set_title('EWI Trigger Frequency', fontweight='bold', color=NAVY, pad=10)
    ax2.set_xlabel('Number of Accounts', color=GRAY)
    ax2.spines[['top','right']].set_visible(False)

    # Panel 3: Score Distribution
    ax3 = axes[1, 0]
    ax3.hist(df['ewi_score'], bins=range(0,13), color=BLUE, edgecolor='white',
             linewidth=0.5, alpha=0.8)
    ax3.axvline(x=3, color=AMBER, linestyle='--', linewidth=2, label='Watch (3+)')
    ax3.axvline(x=5, color=RED, linestyle='--', linewidth=2, label='Action (5+)')
    ax3.set_title('EWI Score Distribution', fontweight='bold', color=NAVY, pad=10)
    ax3.set_xlabel('EWI Score', color=GRAY)
    ax3.set_ylabel('Number of Accounts', color=GRAY)
    ax3.legend(fontsize=9)
    ax3.spines[['top','right']].set_visible(False)

    # Panel 4: RM-wise flagged accounts
    ax4 = axes[1, 1]
    rm_flagged = df[df['ewi_flagged']].groupby('rm_name').size().sort_values(ascending=True)
    ax4.barh(rm_flagged.index, rm_flagged.values,
             color=[RED if v > 5 else AMBER if v > 3 else BLUE
                    for v in rm_flagged.values])
    ax4.set_title('Flagged Accounts by RM', fontweight='bold', color=NAVY, pad=10)
    ax4.set_xlabel('Flagged Accounts', color=GRAY)
    ax4.spines[['top','right']].set_visible(False)

    plt.tight_layout(rect=[0,0,1,0.96])
    plt.savefig('ewi_dashboard.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.show()
    print("\nEWI Dashboard saved as ewi_dashboard.png")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating SME loan portfolio...")
    df = generate_sample_portfolio(n=300)

    print("Scoring Early Warning Indicators...")
    df = score_ewi(df)

    print("\nEWI SUMMARY")
    print("="*50)
    for level in ['Normal', 'Watch', 'Special Mention', 'Immediate Action']:
        count = (df['risk_level'] == level).sum()
        pct = count / len(df) * 100
        print(f"  {level:<20}: {count:>3} accounts ({pct:.1f}%)")
    print(f"\n  Total Flagged (Watch+): {df['ewi_flagged'].sum()} accounts")
    print(f"  Flagged Portfolio:     ₹{df[df['ewi_flagged']]['outstanding_lac'].sum():.0f} Lac")

    action_list = generate_rm_action_list(df)

    print("\nGenerating EWI Dashboard...")
    plot_ewi_dashboard(df)

    # Export to CSV for further analysis
    df.to_csv('portfolio_ewi_scored.csv', index=False)
    print("Full scored portfolio exported to portfolio_ewi_scored.csv")
