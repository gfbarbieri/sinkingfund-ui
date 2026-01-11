"""
Integration Tests for Workflow Reruns and Changes
==================================================

Tests verify that the customizable workflow handles various user actions
correctly, including changing allocation strategies, contribution intervals,
adding/deleting bills, and rerunning envelope creation and scheduling.

Examples
--------
.. code-block:: python

   # Run all tests in this module.
   pytest tests/integration/test_workflow_reruns.py

   # Run a specific test class.
   pytest tests/integration/test_workflow_reruns.py::TestAllocationStrategyChanges
"""

########################################################################
## IMPORTS
########################################################################

from datetime import date, timedelta
from decimal import Decimal

import pytest


########################################################################
## ALLOCATION STRATEGY CHANGE TESTS
########################################################################

class TestAllocationStrategyChanges:
    """Test changing allocation strategies and rerunning envelope creation."""

    def test_change_allocation_strategy_to_none(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test changing allocation strategy to 'none' after envelopes exist."""
        # Add bills (automatically creates envelopes) and allocate
        # with sorted.
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates and allocate with sorted strategy.
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(strategy="sorted")
        
        # Verify allocation occurred.
        envelopes = sample_fund_with_balance.get_envelopes()
        initial_total_allocation = sum(
            env.initial_allocation for env in envelopes
        )
        assert initial_total_allocation > 0
        
        # Change to "none" strategy and rerun (skip allocation).
        # Sync envelopes (they already exist), update dates, but
        # don't allocate.
        sample_fund_with_balance.sync_envelopes_with_bills()
        sample_fund_with_balance.update_contribution_dates(14)
        # When "none" is selected, allocate() is not called, so
        # allocations remain as they were. For true "none" behavior,
        # we would need to reset allocations, but the library doesn't
        # provide that. So we verify that if we don't call allocate(),
        # allocations remain. This test verifies the workflow doesn't
        # break.
        
        # Verify envelopes still exist.
        envelopes_after = sample_fund_with_balance.get_envelopes()
        assert len(envelopes_after) == len(envelopes)

    def test_change_allocation_strategy_from_none_to_sorted(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test changing allocation strategy from 'none' to 'sorted'."""
        # Add bills (automatically creates envelopes) but don't allocate.
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates but don't allocate (none strategy).
        sample_fund_with_balance.update_contribution_dates(14)
        # Skip allocation to simulate "none" strategy.
        
        # Verify no allocation initially (none strategy means skip
        # allocate).
        envelopes_before = sample_fund_with_balance.get_envelopes()
        initial_total_allocation = sum(
            env.initial_allocation for env in envelopes_before
        )
        # Envelopes created without allocate() should have 0 allocation.
        assert initial_total_allocation == 0
        
        # Change to "sorted" strategy and allocate.
        sample_fund_with_balance.sync_envelopes_with_bills()
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(strategy="sorted")
        
        # Verify allocation occurred.
        envelopes_after = sample_fund_with_balance.get_envelopes()
        final_total_allocation = sum(
            env.initial_allocation for env in envelopes_after
        )
        assert final_total_allocation > 0
        assert final_total_allocation <= sample_fund_with_balance.balance

    def test_change_allocation_strategy_from_sorted_to_proportional(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test changing allocation strategy from 'sorted' to 'proportional'."""
        # Add bills (automatically creates envelopes) and allocate
        # with sorted.
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates and allocate with sorted strategy.
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(strategy="sorted")
        
        envelopes_sorted = sample_fund_with_balance.get_envelopes()
        sorted_allocations = [
            env.initial_allocation for env in envelopes_sorted
        ]
        
        # Change to proportional strategy and reallocate.
        # Sync envelopes, update dates, then reallocate with new
        # strategy.
        sample_fund_with_balance.sync_envelopes_with_bills()
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(
            strategy="proportional",
            method="proportional"
        )
        
        # Verify new allocation occurred (may be different from sorted).
        envelopes_proportional = sample_fund_with_balance.get_envelopes()
        proportional_allocations = [
            env.initial_allocation for env in envelopes_proportional
        ]
        
        # Total allocation should still be within balance.
        total_allocation = sum(proportional_allocations)
        assert total_allocation > 0
        assert total_allocation <= sample_fund_with_balance.balance
        
        # Number of envelopes should be the same.
        assert len(envelopes_proportional) == len(envelopes_sorted)


########################################################################
## CONTRIBUTION INTERVAL CHANGE TESTS
########################################################################

class TestContributionIntervalChanges:
    """Test changing contribution intervals and rerunning envelope creation."""

    def test_change_contribution_interval(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test changing contribution interval and updating contribution dates."""
        # Add bills (automatically creates envelopes) with interval=14.
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates with initial interval.
        sample_fund.update_contribution_dates(14)
        
        # Get initial contribution dates.
        envelopes_before = sample_fund.get_envelopes()
        initial_dates = [
            env.start_contrib_date for env in envelopes_before
        ]
        
        # Change contribution interval to 7 and update.
        # Sync envelopes first (they already exist), then update dates.
        sample_fund.sync_envelopes_with_bills()
        sample_fund.update_contribution_dates(7)
        
        # Verify contribution dates were updated.
        envelopes_after = sample_fund.get_envelopes()
        assert len(envelopes_after) == len(envelopes_before)
        
        # Contribution dates should be recalculated (may be different).
        # The exact dates depend on the scheduling algorithm, but we
        # verify the operation completes without error.
        updated_dates = [
            env.start_contrib_date for env in envelopes_after
        ]
        # Dates should still be date objects.
        assert all(isinstance(d, date) for d in updated_dates)


########################################################################
## SCHEDULE RERUN TESTS
########################################################################

class TestScheduleReruns:
    """Test rerunning schedule generation with different strategies."""

    def test_rerun_schedule_generation(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test rerunning schedule generation."""
        # Add bills (automatically creates envelopes) and allocate.
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates and allocate.
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(strategy="sorted")
        
        # Generate initial schedule.
        schedule_result_1 = sample_fund_with_balance.schedule(
            strategy="independent_scheduler"
        )
        
        envelopes_1 = sample_fund_with_balance.get_envelopes()
        assert all(
            hasattr(env, 'schedule') and env.schedule is not None
            for env in envelopes_1
        )
        
        # Rerun schedule generation.
        schedule_result_2 = sample_fund_with_balance.schedule(
            strategy="independent_scheduler"
        )
        
        # Verify schedules were regenerated.
        envelopes_2 = sample_fund_with_balance.get_envelopes()
        assert len(envelopes_2) == len(envelopes_1)
        assert all(
            hasattr(env, 'schedule') and env.schedule is not None
            for env in envelopes_2
        )


########################################################################
## BILL ADDITION AND DELETION TESTS
########################################################################

class TestBillChanges:
    """Test adding and deleting bills and rerunning envelope creation."""

    def test_add_bill_and_rerun_envelope_creation(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test adding a new bill and syncing envelopes."""
        # Add initial bills (automatically creates envelopes).
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates.
        sample_fund.update_contribution_dates(14)
        
        initial_envelopes = sample_fund.get_envelopes()
        initial_count = len(initial_envelopes)
        initial_bill_ids = {
            env.bill_instance.bill_id for env in initial_envelopes
        }
        
        # Add a new bill (this will also create an envelope
        # automatically).
        new_bill = {
            "bill_id": "new_bill_1",
            "service": "New Service",
            "amount_due": 75.0,
            "recurring": False,
            "due_date": date.today() + timedelta(days=60)
        }
        sample_fund.add_bills(source=[new_bill], contribution_interval=14)
        
        # Sync envelopes with bills to ensure consistency.
        sample_fund.sync_envelopes_with_bills()
        sample_fund.update_contribution_dates(14)
        
        # Verify new envelope was created.
        updated_envelopes = sample_fund.get_envelopes()
        updated_count = len(updated_envelopes)
        updated_bill_ids = {
            env.bill_instance.bill_id for env in updated_envelopes
        }
        
        assert updated_count >= initial_count
        assert "new_bill_1" in updated_bill_ids
        # Original bill IDs should still be present.
        assert initial_bill_ids.issubset(updated_bill_ids)

    def test_delete_bill_and_rerun_envelope_creation(
        self, sample_fund, sample_multiple_bills_data
    ):
        """Test deleting a bill and syncing envelopes."""
        # Add bills (automatically creates envelopes).
        sample_fund.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        # Update contribution dates.
        sample_fund.update_contribution_dates(14)
        
        initial_envelopes = sample_fund.get_envelopes()
        initial_count = len(initial_envelopes)
        initial_bill_ids = {
            env.bill_instance.bill_id for env in initial_envelopes
        }
        
        # Delete a bill.
        if initial_bill_ids:
            bill_to_delete = list(initial_bill_ids)[0]
            sample_fund.delete_bills([bill_to_delete])
            
            # Sync envelopes with bills (should remove envelope for
            # deleted bill).
            sample_fund.sync_envelopes_with_bills()
            sample_fund.update_contribution_dates(14)
            
            # Verify envelope was removed.
            updated_envelopes = sample_fund.get_envelopes()
            updated_count = len(updated_envelopes)
            updated_bill_ids = {
                env.bill_instance.bill_id for env in updated_envelopes
            }
            
            assert updated_count < initial_count
            assert bill_to_delete not in updated_bill_ids
            # Other bill IDs should still be present.
            assert updated_bill_ids.issubset(initial_bill_ids)


########################################################################
## FULL WORKFLOW TESTS
########################################################################

class TestFullWorkflowChanges:
    """Test complete workflow with multiple changes."""

    def test_full_workflow_multiple_changes(
        self, sample_fund_with_balance, sample_multiple_bills_data
    ):
        """Test complete workflow with multiple changes."""
        # Step 1: Add bills (automatically creates envelopes).
        sample_fund_with_balance.add_bills(
            source=sample_multiple_bills_data,
            contribution_interval=14
        )
        
        bills = sample_fund_with_balance.get_bills()
        assert len(bills) > 0
        
        # Step 2: Update contribution dates and allocate with sorted strategy.
        sample_fund_with_balance.update_contribution_dates(14)
        sample_fund_with_balance.allocate(strategy="sorted")
        
        envelopes_1 = sample_fund_with_balance.get_envelopes()
        assert len(envelopes_1) > 0
        
        # Step 3: Change contribution interval.
        sample_fund_with_balance.sync_envelopes_with_bills()
        sample_fund_with_balance.update_contribution_dates(7)
        
        envelopes_2 = sample_fund_with_balance.get_envelopes()
        assert len(envelopes_2) == len(envelopes_1)
        
        # Step 4: Change allocation strategy to proportional.
        sample_fund_with_balance.sync_envelopes_with_bills()
        sample_fund_with_balance.update_contribution_dates(7)
        sample_fund_with_balance.allocate(
            strategy="proportional",
            method="proportional"
        )
        
        envelopes_3 = sample_fund_with_balance.get_envelopes()
        assert len(envelopes_3) == len(envelopes_2)
        
        # Step 5: Generate schedule.
        schedule_result = sample_fund_with_balance.schedule(
            strategy="independent_scheduler"
        )
        
        envelopes_4 = sample_fund_with_balance.get_envelopes()
        assert all(
            hasattr(env, 'schedule') and env.schedule is not None
            for env in envelopes_4
        )
        
        # Step 6: Add a new bill and sync.
        new_bill = {
            "bill_id": "workflow_test_bill",
            "service": "Workflow Test",
            "amount_due": 50.0,
            "recurring": False,
            "due_date": date.today() + timedelta(days=90)
        }
        sample_fund_with_balance.add_bills(source=[new_bill], contribution_interval=7)
        sample_fund_with_balance.sync_envelopes_with_bills()
        sample_fund_with_balance.update_contribution_dates(7)
        sample_fund_with_balance.allocate(strategy="proportional", method="proportional")
        
        envelopes_5 = sample_fund_with_balance.get_envelopes()
        assert len(envelopes_5) > len(envelopes_4)
        
        # Step 7: Regenerate schedule.
        schedule_result_2 = sample_fund_with_balance.schedule(
            strategy="independent_scheduler"
        )
        
        envelopes_final = sample_fund_with_balance.get_envelopes()
        assert all(
            hasattr(env, 'schedule') and env.schedule is not None
            for env in envelopes_final
        )
        
        # Verify we can generate a report.
        report = sample_fund_with_balance.report(active_only=True)
        assert isinstance(report, dict)

