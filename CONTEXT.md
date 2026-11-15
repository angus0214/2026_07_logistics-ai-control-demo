# Logistics AI Control Tower Glossary

## Core Layout Concepts

* **Off-canvas Drawer**: The mobile responsive pattern for the Left Sidebar. The navigation remains hidden off-screen and slides over the main content when triggered by a hamburger menu.
* **Modal/Sheet Overlay**: The mobile responsive pattern for the Right Panel (Original Document Preview). Rather than stacking vertically below the main table, it appears as a full-screen or bottom-sheet overlay when the user actively requests to "View Document".
* **Graceful Degradation**: The concept of hiding or simplifying complex Desktop UI elements on mobile devices, which we explicitly decided *against* for this project in favor of retaining full functionality via overlays.

## Shipments & Billing

**B/L Number（提單號）**:
The single identifier of a shipment, shared by the operations system and the finance system; only its spelling/formatting differs between them.
_Avoid_: HBL, MBL (this demo does not distinguish the two levels)

**Freight Ledger（運費帳）**:
The raw export from the finance system, kept exactly as received — messy names, mixed currencies, inconsistent dates.
_Avoid_: finance table, billing table

**Charge Line（費用明細）**:
One billed item for one B/L Number (e.g. ocean freight, THC, a credit note); a shipment usually has several.
_Avoid_: invoice row, record

**Quoted Freight（報價運費）**:
The freight amount printed on the bill of lading document, as extracted by OCR.
_Avoid_: freight cost, 運費 (unqualified)

**Billed Amount（請款金額）**:
The sum of a shipment's Charge Lines, converted to USD at the invoice month's rate. This is what an unqualified "運費" means.
_Avoid_: revenue, actual freight

**Credit Note（沖銷）**:
A Charge Line that reduces what the Customer owes; it always counts negatively toward the Billed Amount, however the raw export writes its sign.
_Avoid_: refund, discount

**Invoice Date（發票日）**:
The date the finance system billed a Charge Line; it decides which month's FX rate applies.
_Avoid_: billing date

**On-board Date（開航日）**:
The date the shipment sailed. Time-period questions ("上個月運費") are answered by On-board Date unless Invoice Date is asked for explicitly, so unmatched Charge Lines fall outside any period.
_Avoid_: ship date, ETD

**Customer（客戶）**:
The party billed for a shipment; in this demo always the Shipper, since every shipment is assumed prepaid.
_Avoid_: bill-to, consignee, client

**Data Dictionary（資料字典）**:
The single written definition of every queryable field and business rule (what "運費" means, which date defines a period, which table answers what). Read by humans and by the Agent alike.
_Avoid_: schema doc, metadata

**Query Evidence（查詢依據）**:
The raw result of the last SQL the Agent ran for an answer, shown as a table under the summary. Its numbers come straight from the database, never retyped by the LLM, and it is the same query the Eval Set scores.
_Avoid_: result table, data table

**Unmapped Customer（未對應客戶）**:
A customer name in the Freight Ledger with no known alias; it is kept under its raw spelling and flagged, never blanked.
_Avoid_: unknown customer

**Match Status（對帳狀態）**:
Whether a Charge Line's B/L Number links to a known shipment: exactly, only after format normalisation, or not at all. Unmatched lines are kept, never dropped.
_Avoid_: orphan, error row

## Evaluation

**Eval Set（評估集）**:
A fixed list of boss-style questions, each with one Gold Answer, asked against a freshly seeded, frozen dataset. Questions name explicit months, never relative time.
_Avoid_: test cases, benchmark

**Gold Answer（標準答案）**:
The single correct result for an Eval Set question, derived from the clean source data before it was dirtied — never from the cleaned view.
_Avoid_: expected output

**Arm（對照組）**:
One configuration the Eval Set is run against: **Raw** (the Freight Ledger in place of the cleaned view), **Raw + Dictionary**, or **View + Dictionary**. Every Arm also sees the bills of lading. Comparing Arms separates what the cleaned view contributes from what the Data Dictionary contributes.
_Avoid_: variant, mode
