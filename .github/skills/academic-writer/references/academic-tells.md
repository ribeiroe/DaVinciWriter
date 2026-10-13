# Academic Tells — Drafting-Time Checklist

This is the drafting-time subset of the humanizer patterns: the academic-specific tells plus the overused AI-vocabulary list.
The full pattern reference (`humanizer.md`) is used by /check-quality; apply this file while drafting sections.
Fix every instance before saving a section.

## Overused AI vocabulary

**High-frequency AI words:** Actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adjective), landscape (abstract noun), pivotal, showcase, tapestry (abstract noun), testament, underscore (verb), valuable, vibrant

These words appear far more frequently in post-2023 text, and they often co-occur ("...underscoring the pivotal interplay across the evolving landscape..."). Replace them with plain alternatives.

## Academic writing patterns

### 1. Academic AI boilerplate openers

**Phrases to watch:** "In recent years,", "With the rapid development of", "In the era of", "As X continues to grow", "The widespread adoption of"

LLMs open academic sections with sweeping temporal claims that add no information. Anchor the opening in a specific fact, gap, or consequence instead.

**Before:**
> In recent years, deep learning has transformed the field of natural language processing. With the rapid development of large language models, researchers have increasingly focused on few-shot learning.

**After:**
> Few-shot learning has become a practical necessity as deployment costs for large language models rise. Fine-tuning a model for each downstream task is expensive at scale.

### 2. "To the best of our knowledge"

Widely overused in AI-generated papers. Use it only when genuinely claiming a first — and only once per paper.

**Before:**
> To the best of our knowledge, this is the first work to apply attention mechanisms to sensor fusion. To the best of our knowledge, no prior method achieves this simultaneously.

**After:**
> Prior work has applied attention to individual modalities separately; we are not aware of a method that fuses heterogeneous sensors within a single attention block.

### 3. Overuse of "novel", "state-of-the-art", "comprehensive", and "extensive"

**Words to watch:** novel, state-of-the-art (as a self-description), comprehensive, extensive, thorough, rigorous (applied to own work)

LLMs self-congratulate. Reviewers flag these as empty claims. Let the results speak; do not editorialize.

**Before:**
> We propose a novel and comprehensive framework that achieves state-of-the-art results through rigorous experimentation.

**After:**
> Our framework achieves 94.3 F1 on the SQuAD benchmark, 1.2 points above the previous best.

### 4. Contribution list inflation

LLMs pad contribution lists with trivial or circular items.

**Before:**
> Our contributions are as follows: (1) We propose a new method. (2) We conduct extensive experiments. (3) We show that our method works. (4) We release code.

**After:**
> Our contributions are: (1) a cross-modal attention block that fuses RGB and depth features without auxiliary supervision; (2) a new benchmark of 4,200 annotated samples with sensor noise; (3) a 3.1-point improvement over the prior best on NYU-Depth v2.

### 5. Circular methodology descriptions

AI describes methodology by restating the section heading rather than explaining the mechanism.

**Before:**
> Our method processes the input by applying a processing step. The network learns a representation by encoding the data into a latent space, which is then decoded.

**After:**
> A 512-dim transformer encoder maps each token to a context vector; a three-layer MLP then predicts the class label from the [CLS] token.

### 6. Vague baseline comparisons

LLMs compare against "existing methods" or "baseline approaches" without naming them.

**Before:**
> Our method outperforms existing methods on all benchmarks, demonstrating significant improvements over baseline approaches.

**After:**
> Our method outperforms BERT-base (+2.1 F1), RoBERTa-large (+0.8 F1), and DeBERTa-v3 (+0.3 F1) on GLUE.

### 7. "It is worth noting that" and hedging throat-clears

**Phrases to watch:** "It is worth noting that", "It should be noted that", "It is important to mention", "We note that", "Notably,", "Interestingly,"

These phrases are filler. Either the observation is important enough to state directly, or it should be cut.

**Before:**
> It is worth noting that the model performs differently on out-of-distribution data. Notably, the degradation is more severe for longer sequences.

**After:**
> Performance drops by 6.4 F1 on out-of-distribution data, with a further 2.1-point penalty for sequences longer than 512 tokens.

### 8. Overloaded related work summaries

LLMs summarize related work as a list of "X proposed Y, Z proposed W" sentences with no synthesis.

**Before:**
> Smith et al. [1] proposed a transformer-based approach. Jones et al. [2] used convolutional networks. Brown et al. [3] combined both approaches. Our work is related to all of these.

**After:**
> Transformer-based methods [1, 4, 7] dominate the leaderboard but require full fine-tuning. CNN-based methods [2, 5] are faster at inference but degrade beyond 256-token inputs. We build on [3], which combines both, and add a gating mechanism to control which modality dominates at each layer.

## Quick style sweep

Also check for: em dash overuse (rewrite with commas, periods, or parentheses), rule-of-three lists forced for rhythm, inline bold headers in vertical lists, superficial "-ing" tack-ons ("highlighting...", "underscoring..."), and copula avoidance ("serves as" instead of "is").
